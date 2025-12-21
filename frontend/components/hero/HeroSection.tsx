"use client";

import { motion } from "framer-motion";
import { PlayCircle } from "lucide-react";
import ParticleEffect from "./ParticleEffect";

import { useRouter } from "next/navigation";

export default function HeroSection() {
    const router = useRouter();
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
            {/* Background Grid */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px]" />

            {/* Particle Effect */}
            <ParticleEffect />

            {/* Content */}
            <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-5xl md:text-7xl font-bold mb-6">
                        Agentic Wafer{" "}
                        <br />
                        <span className="text-gradient-cyan">Defect Analysis</span>
                    </h1>
                </motion.div>

                <motion.p
                    className="text-lg md:text-xl text-text-secondary max-w-3xl mx-auto mb-12"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                >
                    Leveraging computer vision to identify yield-killing defects in real-time with
                    nanometer precision. Transform your inspection workflow today.
                </motion.p>

                <motion.div
                    className="flex flex-col sm:flex-row items-center justify-center gap-4"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                >
                    <button
                        onClick={() => router.push('/analysis')}
                        className="bg-primary-cyan hover:bg-primary-dark text-background px-8 py-4 rounded-lg font-semibold text-lg transition glow-cyan flex items-center gap-2 group"
                    >
                        Analyze Wafer
                        <span className="group-hover:translate-x-1 transition-transform">→</span>
                    </button>

                    <button className="border-2 border-primary-cyan text-primary-cyan hover:bg-primary-cyan/10 px-8 py-4 rounded-lg font-semibold text-lg transition flex items-center gap-2">
                        <PlayCircle className="w-5 h-5" />
                        View Demo
                    </button>
                </motion.div>

                <motion.p
                    className="text-text-tertiary text-sm mt-12"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                >
                    TRUSTED BY INDUSTRY LEADERS
                </motion.p>
            </div>
        </section>
    );
}
