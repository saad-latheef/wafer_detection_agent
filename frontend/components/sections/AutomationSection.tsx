"use client";

import { motion } from "framer-motion";
import { AlertOctagon, Ban, ShieldAlert, XCircle } from "lucide-react";
import HolographicCard from "@/components/ui/HolographicCard";

const automationFailures = [
    {
        icon: Ban,
        title: "Rigid Rule Sets",
        description: "Traditional automation fails when encountering novel defects not predefined in the codebase.",
    },
    {
        icon: XCircle,
        title: "Zero Adaptability",
        description: "Static scripts cannot learn from new data, requiring constant manual updates and maintenance.",
    },
    {
        icon: AlertOctagon,
        title: "Context Blindness",
        description: "Automation lacks the semantic understanding to distinguish between critical defects and noise.",
    },
    {
        icon: ShieldAlert,
        title: "Fragile Pipelines",
        description: "One unexpected variable can break the entire inspection chain, causing production halts.",
    },
];

import { MaskedReveal, HighlightSwipe } from "@/components/ui/TextAnimations";

// ... existing imports ...

export default function AutomationSection() {
    return (
        <section className="py-24 bg-transparent relative z-10">
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-6 flex flex-col items-center justify-center gap-2">
                        <MaskedReveal>
                            Why
                        </MaskedReveal>
                        <MaskedReveal delay={0.2}>
                            <HighlightSwipe highlightColor="text-red-500">
                                Automation Alone Fails
                            </HighlightSwipe>
                        </MaskedReveal>
                    </h2>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        Scripts and basic ML models crumble under the complexity of modern fab environments.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {automationFailures.map((failure, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: false, margin: "-100px" }}
                        >
                            <HolographicCard
                                className="h-full p-8 border-red-500/10 hover:border-red-500/30 hover:shadow-red-500/10"
                                spotlightColor="rgba(255, 0, 85, 0.15)"
                            >
                                <failure.icon className="w-10 h-10 text-red-500 mb-6" />
                                <h3 className="text-xl font-semibold mb-3 text-white">
                                    {failure.title}
                                </h3>
                                <p className="text-gray-400 leading-relaxed">
                                    {failure.description}
                                </p>
                            </HolographicCard>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
