"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register GSAP plugin
if (typeof window !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
}

const steps = [
    {
        number: "01",
        title: "Wafer Fabrication",
        description: "Raw silicon ingot slicing and polishing using legacy machinery.",
    },
    {
        number: "02",
        title: "Initial Inspection",
        description: "Manual optical microscopy review performed by human operators.",
    },
    {
        number: "03",
        title: "Defect Classification",
        description: "Operator-dependent categorization of anomalies with high variance.",
        active: true,
    },
    {
        number: "04",
        title: "Root Cause Analysis",
        description: "Historical data cross-referencing using disconnected spreadsheets.",
    },
    {
        number: "05",
        title: "Yield Decision",
        description: "Final go/no-go determination based on sample size extrapolation.",
    },
];

export default function WorkflowSection() {
    const sectionRef = useRef(null);
    const titleRef = useRef(null);
    const stepsRef = useRef(null);
    const isInView = useInView(sectionRef, { once: true, margin: "-100px" });
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        // Check if mobile
        const checkMobile = () => {
            setIsMobile(window.innerWidth < 1024);
        };
        checkMobile();
        window.addEventListener("resize", checkMobile);

        // Only apply scroll trigger on desktop
        if (!isMobile && titleRef.current && stepsRef.current && sectionRef.current) {
            const ctx = gsap.context(() => {
                // Pin the title while the steps scroll
                ScrollTrigger.create({
                    trigger: sectionRef.current,
                    start: "top top",
                    end: "bottom bottom",
                    pin: titleRef.current,
                    pinSpacing: false,
                });

                // Animate steps as they come into view
                gsap.utils.toArray(".workflow-step").forEach((step: any, index) => {
                    gsap.fromTo(
                        step,
                        {
                            opacity: 0.3,
                            x: 50,
                        },
                        {
                            opacity: 1,
                            x: 0,
                            scrollTrigger: {
                                trigger: step,
                                start: "top center",
                                end: "bottom center",
                                scrub: true,
                            },
                        }
                    );
                });
            }, sectionRef);

            return () => {
                ctx.revert();
                window.removeEventListener("resize", checkMobile);
            };
        }

        return () => {
            window.removeEventListener("resize", checkMobile);
        };
    }, [isMobile]);

    // Mobile layout (original design)
    if (isMobile) {
        return (
            <section ref={sectionRef} className="py-24 px-6">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-16">
                        <p className="text-text-tertiary text-sm tracking-widest mb-4">CURRENT WORKFLOW</p>
                        <h2 className="text-4xl md:text-5xl font-bold">Manual Workflow Limitations</h2>
                        <p className="text-text-secondary mt-6 text-lg max-w-2xl mx-auto">
                            The traditional process relies heavily on human intervention,
                            leading to inconsistencies and bottlenecks.
                        </p>
                    </div>

                    {/* Timeline */}
                    <div className="relative">
                        {/* Connecting Line */}
                        <div className="absolute left-1/2 transform -translate-x-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-primary/50 to-transparent" />

                        {/* Steps */}
                        <div className="space-y-8">
                            {steps.map((step, index) => (
                                <motion.div
                                    key={step.number}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                                    transition={{ duration: 0.6, delay: index * 0.1 }}
                                    className={`relative flex items-center ${index % 2 === 0 ? "flex-row" : "flex-row-reverse"
                                        }`}
                                >
                                    {/* Content */}
                                    <div className={`w-5/12 ${index % 2 === 0 ? "text-right pr-12" : "text-left pl-12"}`}>
                                        <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                                        <p className="text-text-secondary">{step.description}</p>
                                    </div>

                                    {/* Node */}
                                    <div className="absolute left-1/2 transform -translate-x-1/2 w-16 h-16 flex items-center justify-center">
                                        <div
                                            className={`w-12 h-12 rounded-full border-2 flex items-center justify-center font-bold text-sm ${step.active
                                                    ? "bg-primary border-primary text-background glow-cyan"
                                                    : "bg-background-card border-white/20 text-text-secondary"
                                                }`}
                                        >
                                            {step.number}
                                        </div>
                                    </div>

                                    {/* Spacer */}
                                    <div className="w-5/12" />
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    {/* Footer */}
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={isInView ? { opacity: 1 } : {}}
                        transition={{ duration: 0.8, delay: 0.6 }}
                        className="text-center mt-16 text-2xl font-semibold"
                    >
                        High effort. High delay.{" "}
                        <span className="text-primary">High subjectivity.</span>
                    </motion.p>
                </div>
            </section>
        );
    }

    // Desktop layout with scroll pinning
    return (
        <section ref={sectionRef} className="py-24 px-6 min-h-[200vh]">
            <div className="max-w-7xl mx-auto">
                <div className="grid lg:grid-cols-2 gap-16">
                    {/* Left: Pinned Title */}
                    <div ref={titleRef} className="lg:sticky lg:top-24 lg:h-fit">
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            animate={isInView ? { opacity: 1, x: 0 } : {}}
                            transition={{ duration: 0.8 }}
                        >
                            <p className="text-text-tertiary text-sm tracking-widest mb-4">CURRENT WORKFLOW</p>
                            <h2 className="text-4xl md:text-5xl font-bold mb-6">
                                Manual Workflow Limitations
                            </h2>
                            <p className="text-text-secondary text-lg">
                                The traditional process relies heavily on human intervention,
                                leading to inconsistencies and bottlenecks.
                            </p>

                            <div className="mt-12 p-6 bg-background-card rounded-lg border border-primary/30">
                                <p className="text-2xl font-semibold">
                                    High effort. High delay.{" "}
                                    <span className="text-primary">High subjectivity.</span>
                                </p>
                            </div>
                        </motion.div>
                    </div>

                    {/* Right: Scrollable Steps */}
                    <div ref={stepsRef} className="space-y-12 py-12">
                        {steps.map((step, index) => (
                            <div
                                key={step.number}
                                className="workflow-step p-8 bg-background-card rounded-lg border border-white/10 hover:border-primary/50 transition-all"
                            >
                                <div className="flex items-start gap-6">
                                    <div
                                        className={`w-16 h-16 rounded-full border-2 flex items-center justify-center font-bold text-xl flex-shrink-0 ${step.active
                                                ? "bg-primary border-primary text-background glow-cyan"
                                                : "bg-background-darker border-white/20 text-text-secondary"
                                            }`}
                                    >
                                        {step.number}
                                    </div>
                                    <div>
                                        <h3 className="text-2xl font-semibold mb-3">{step.title}</h3>
                                        <p className="text-text-secondary text-lg">{step.description}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
