"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";

export default function DataStream() {
    const { scrollYProgress } = useScroll();
    const scaleY = useSpring(scrollYProgress, {
        stiffness: 100,
        damping: 30,
        restDelta: 0.001
    });

    return (
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
            {/* Central Line Container */}
            <div className="absolute left-1/2 top-0 bottom-0 w-px -translate-x-1/2 h-full">

                {/* Base Line (Faint) */}
                <div className="absolute inset-0 w-full bg-cyan-900/20" />

                {/* Progress Line (Glowing) - follows scroll */}
                <motion.div
                    className="absolute top-0 left-0 w-full bg-cyan-500 shadow-[0_0_15px_rgba(0,212,255,0.5)]"
                    style={{ scaleY, transformOrigin: "top" }}
                />

                {/* Animated Data Packets */}
                <div className="absolute inset-0 w-full overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1 h-20 bg-gradient-to-b from-transparent via-cyan-400 to-transparent animate-data-stream opacity-75 blur-[1px]" />
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1 h-32 bg-gradient-to-b from-transparent via-cyan-300 to-transparent animate-data-stream opacity-50 blur-[2px]" style={{ animationDelay: "2s" }} />
                </div>
            </div>
        </div>
    );
}
