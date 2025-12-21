"use client";

import Link from "next/link";
import { Cpu } from "lucide-react";

export default function Navigation() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-white/10">
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 text-xl font-bold">
                        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                            <Cpu className="w-5 h-5 text-background" />
                        </div>
                        <span>AgenticWafer</span>
                    </Link>

                    {/* Menu Items */}
                    <div className="hidden md:flex items-center gap-8">
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Platform
                        </Link>
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Solutions
                        </Link>
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Resources
                        </Link>
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Contact
                        </Link>
                    </div>

                    {/* CTA Button */}
                    <button className="bg-primary hover:bg-primary-dark text-background px-6 py-2 rounded-lg font-semibold transition hover:glow-cyan">
                        Request Demo
                    </button>
                </div>
            </div>
        </nav>
    );
}
