"use client";

import { motion } from "framer-motion";
import { AlertCircle, EyeOff, FileWarning, Hourglass } from "lucide-react";
import HolographicCard from "@/components/ui/HolographicCard";

const problems = [
    {
        icon: EyeOff,
        title: "Manual Inspection Limits",
        description: "Human operators miss up to 30% of micro-defects due to fatigue and optical limitations.",
    },
    {
        icon: Hourglass,
        title: "Slow Feedback Loops",
        description: "Traditional AOI systems take hours to process batches, delaying critical yield decisions.",
    },
    {
        icon: FileWarning,
        title: "False Positives",
        description: "Legacy rule-based systems flag non-critical variations, wasting valuable engineering time.",
    },
    {
        icon: AlertCircle,
        title: "Data Silos",
        description: "Defect data remains isolated from fabrication parameters, preventing root cause analysis.",
    },
];

import { MaskedReveal, HighlightSwipe } from "@/components/ui/TextAnimations";

// ... existing imports ...

export default function ProblemSection() {
    return (
        <section className="py-24 bg-transparent relative z-10">
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-6 flex flex-col items-center justify-center gap-2">
                        <MaskedReveal>
                            Why wafer inspection
                        </MaskedReveal>
                        <MaskedReveal delay={0.2}>
                            <HighlightSwipe highlightColor="text-cyan-400">
                                breaks at scale
                            </HighlightSwipe>
                        </MaskedReveal>
                    </h2>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        As nodes shrink to angstrom levels, traditional inspection methods essentially fly blind.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {problems.map((problem, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: false, margin: "-100px" }}
                        >
                            <HolographicCard className="h-full p-8">
                                <problem.icon className="w-10 h-10 text-primary mb-6" />
                                <h3 className="text-xl font-semibold mb-3 text-white">
                                    {problem.title}
                                </h3>
                                <p className="text-gray-400 leading-relaxed">
                                    {problem.description}
                                </p>
                            </HolographicCard>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
