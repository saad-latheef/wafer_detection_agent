"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import Image from "next/image";
import { ArrowDown, Upload, Zap, Crosshair, Shield } from "lucide-react";
// ...
{/* Pulsing Arrow Animation */ }
<div className="flex flex-col items-center gap-2 animate-bounce text-primary-cyan/80">
    <span className="text-xs font-medium uppercase tracking-widest opacity-70">Start Here</span>
    <ArrowDown className="w-6 h-6" />
</div>

interface LiveDemoSectionProps {
    onStartAnalysis?: () => void;
}

export default function LiveDemoSection({ onStartAnalysis }: LiveDemoSectionProps) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });

    return (
        <section ref={ref} className="relative flex w-full flex-col items-center justify-center overflow-hidden py-24 bg-background">
            {/* Wafer Background Image */}
            <div className="absolute top-[5%] left-1/2 -translate-x-1/2 w-[900px] h-[900px] pointer-events-none select-none opacity-30 z-0">
                <div className="relative w-full h-full [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_70%)]">
                    <Image
                        src="/wafer-bg.png"
                        alt="Silicon Wafer Background"
                        fill
                        className="object-contain"
                        priority
                    />
                </div>
            </div>

            {/* Content Container */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8 }}
                className="relative z-10 mx-auto flex max-w-4xl flex-col items-center px-4 text-center"
            >
                {/* Badge */}
                <div className="mb-6 inline-flex items-center rounded-full border border-primary-cyan/20 bg-primary-cyan/5 px-3 py-1 backdrop-blur-md">
                    <span className="flex size-2 rounded-full bg-primary-cyan animate-pulse mr-2"></span>
                    <span className="text-xs font-semibold uppercase tracking-wider text-primary-cyan">Live Demo Available</span>
                </div>

                {/* Heading */}
                <h2 className="mb-6 text-4xl font-black leading-tight tracking-tight text-white sm:text-5xl md:text-6xl">
                    See it in <span className="text-gradient-cyan">action</span>
                </h2>

                {/* Subheading */}
                <p className="mb-12 max-w-2xl text-base font-normal leading-relaxed text-text-secondary sm:text-lg md:text-xl">
                    Upload a sample wafer image and let our AI identify defects with sub-micron precision in seconds. Experience enterprise-grade analysis instantly.
                </p>

                {/* Interactive Area */}
                <div className="flex flex-col items-center justify-center gap-4">
                    {/* Pulsing Arrow Animation */}
                    <div className="flex flex-col items-center gap-2 animate-bounce text-primary-cyan/80">
                        <span className="text-xs font-medium uppercase tracking-widest opacity-70">Start Here</span>
                        <ArrowDown className="w-6 h-6" />
                    </div>

                    {/* CTA Button */}
                    <button
                        onClick={onStartAnalysis}
                        className="group relative flex h-14 min-w-[200px] cursor-pointer items-center justify-center overflow-hidden rounded-xl bg-primary-cyan px-8 text-base font-bold text-background shadow-[0_0_20px_rgba(0,212,255,0.2)] transition-all hover:scale-105 hover:bg-primary-dark hover:shadow-[0_0_40px_rgba(0,212,255,0.4)] focus:outline-none focus:ring-4 focus:ring-primary-cyan/30"
                    >
                        <Upload className="mr-2 w-5 h-5 transition-transform group-hover:-translate-y-1" />
                        <span className="relative z-10">Analyze Wafer</span>
                        <div className="absolute inset-0 -z-10 translate-y-full bg-white/20 transition-transform duration-300 group-hover:translate-y-0"></div>
                    </button>

                    <p className="mt-4 text-xs text-text-tertiary">
                        No credit card required • 14-day free trial for enterprise
                    </p>
                </div>
            </motion.div>

            {/* Features Grid */}
            <div className="w-full max-w-7xl px-4 sm:px-6 lg:px-8 mt-20 relative z-10">
                <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
                    {/* Feature 1 */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={isInView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="rounded-2xl border border-white/5 bg-background-card p-8 backdrop-blur-sm transition-colors hover:border-primary-cyan/30"
                    >
                        <div className="mb-4 inline-flex rounded-lg bg-primary-cyan/20 p-3 text-primary-cyan">
                            <Zap className="w-6 h-6" />
                        </div>
                        <h3 className="mb-2 text-xl font-bold text-white">Real-time Analysis</h3>
                        <p className="text-text-secondary">Process thousands of wafers per hour with our optimized inference engine.</p>
                    </motion.div>

                    {/* Feature 2 */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={isInView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className="rounded-2xl border border-white/5 bg-background-card p-8 backdrop-blur-sm transition-colors hover:border-primary-cyan/30"
                    >
                        <div className="mb-4 inline-flex rounded-lg bg-primary-cyan/20 p-3 text-primary-cyan">
                            <Crosshair className="w-6 h-6" />
                        </div>
                        <h3 className="mb-2 text-xl font-bold text-white">Sub-micron Accuracy</h3>
                        <p className="text-text-secondary">Detect defects smaller than 1 micron with 99.9% classification accuracy.</p>
                    </motion.div>

                    {/* Feature 3 */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={isInView ? { opacity: 1, y: 0 } : {}}
                        transition={{ duration: 0.6, delay: 0.6 }}
                        className="rounded-2xl border border-white/5 bg-background-card p-8 backdrop-blur-sm transition-colors hover:border-primary-cyan/30"
                    >
                        <div className="mb-4 inline-flex rounded-lg bg-primary-cyan/20 p-3 text-primary-cyan">
                            <Shield className="w-6 h-6" />
                        </div>
                        <h3 className="mb-2 text-xl font-bold text-white">Enterprise Security</h3>
                        <p className="text-text-secondary">SOC2 compliant infrastructure ensures your proprietary designs remain secure.</p>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
