"use client";

import { motion } from "framer-motion";
import { Activity, Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: "smooth" });
            setMobileMenuOpen(false);
        }
    };

    return (
        <motion.header
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-background/80 border-b border-white/10"
        >
            <div className="container mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary-cyan to-primary flex items-center justify-center">
                            <Activity className="h-6 w-6 text-background" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gradient-cyan">AgentWafer</h1>
                            <p className="text-xs text-muted-foreground">AI-Powered Analysis</p>
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-8">
                        <button
                            onClick={() => scrollToSection("problem")}
                            className="text-sm text-foreground/80 hover:text-primary-cyan transition-colors"
                        >
                            Problem
                        </button>
                        <button
                            onClick={() => scrollToSection("workflow")}
                            className="text-sm text-foreground/80 hover:text-primary-cyan transition-colors"
                        >
                            Workflow
                        </button>
                        <button
                            onClick={() => scrollToSection("agents")}
                            className="text-sm text-foreground/80 hover:text-primary-cyan transition-colors"
                        >
                            Agents
                        </button>
                        <button
                            onClick={() => scrollToSection("demo")}
                            className="text-sm text-foreground/80 hover:text-primary-cyan transition-colors"
                        >
                            Live Demo
                        </button>
                        <Button
                            onClick={() => window.location.href = "/analysis"}
                            className="bg-gradient-to-r from-primary-cyan to-primary hover:opacity-90 transition-opacity"
                        >
                            Get Started
                        </Button>
                    </nav>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden p-2 text-foreground"
                    >
                        {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                    </button>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden mt-4 pb-4 space-y-3"
                    >
                        <button
                            onClick={() => scrollToSection("problem")}
                            className="block w-full text-left px-4 py-2 text-sm text-foreground/80 hover:text-primary-cyan hover:bg-white/5 rounded transition-colors"
                        >
                            Problem
                        </button>
                        <button
                            onClick={() => scrollToSection("workflow")}
                            className="block w-full text-left px-4 py-2 text-sm text-foreground/80 hover:text-primary-cyan hover:bg-white/5 rounded transition-colors"
                        >
                            Workflow
                        </button>
                        <button
                            onClick={() => scrollToSection("agents")}
                            className="block w-full text-left px-4 py-2 text-sm text-foreground/80 hover:text-primary-cyan hover:bg-white/5 rounded transition-colors"
                        >
                            Agents
                        </button>
                        <button
                            onClick={() => scrollToSection("demo")}
                            className="block w-full text-left px-4 py-2 text-sm text-foreground/80 hover:text-primary-cyan hover:bg-white/5 rounded transition-colors"
                        >
                            Live Demo
                        </button>
                        <Button
                            onClick={() => window.location.href = "/analysis"}
                            className="w-full bg-gradient-to-r from-primary-cyan to-primary hover:opacity-90 transition-opacity"
                        >
                            Get Started
                        </Button>
                    </motion.div>
                )}
            </div>
        </motion.header>
    );
}
