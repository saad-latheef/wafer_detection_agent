"use client";

import { motion } from "framer-motion";
import { BrainCircuit, Database, LineChart, Cpu } from "lucide-react";
import OrbitalSystem from "@/components/animations/OrbitalSystem";
import HolographicCard from "@/components/ui/HolographicCard";

const agents = [
    {
        icon: Database,
        title: "Ingestion Agent",
        description: "High-throughput data pipeline normalizing multi-sourced metrology data in real-time.",
    },
    {
        icon: BrainCircuit,
        title: "Detection Agent",
        description: "Advanced CNN models focusing on micro-defect identification with <1% false positive rate.",
    },
    {
        icon: LineChart,
        title: "Analysis Agent",
        description: "Statistical correlation engine linking defect patterns to specific process tool excursions.",
    },
    {
        icon: Cpu,
        title: "Master Agent",
        description: "Orchestration layer converting agent insights into verified yield-improvement actions.",
    },
];

import { MaskedReveal, HighlightSwipe } from "@/components/ui/TextAnimations";

// ... existing imports ...

export default function AgenticSection() {
    return (
        <section className="py-24 bg-transparent relative z-10">
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white flex flex-col items-center justify-center gap-2">
                        <MaskedReveal>
                            Decision-making
                        </MaskedReveal>
                        <MaskedReveal delay={0.2}>
                            <HighlightSwipe highlightColor="text-cyan-400">
                                intelligence
                            </HighlightSwipe>
                        </MaskedReveal>
                    </h2>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        A multi-agent system that replicates expert engineering intuition at infinite scale.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Diagram */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.8 }}
                        viewport={{ once: false, margin: "-100px" }}
                        className="bg-gray-900/30 rounded-3xl p-6 border border-white/5 backdrop-blur-sm"
                    >
                        <OrbitalSystem />
                    </motion.div>

                    {/* Agent Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {agents.map((agent, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: 20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                viewport={{ once: false, margin: "-50px" }}
                            >
                                <HolographicCard className="h-full p-6">
                                    <agent.icon className="w-8 h-8 text-primary mb-4" />
                                    <h3 className="text-lg font-semibold mb-2 text-white">
                                        {agent.title}
                                    </h3>
                                    <p className="text-sm text-gray-400 leading-relaxed">
                                        {agent.description}
                                    </p>
                                </HolographicCard>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
