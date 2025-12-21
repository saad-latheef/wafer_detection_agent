"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useState, useEffect } from "react";
import { cn } from "@/lib/utils";

// 1. Masked Reveal (Slide up from invisible line)
export const MaskedReveal = ({
    children,
    className,
    delay = 0,
}: {
    children: React.ReactNode;
    className?: string;
    delay?: number;
}) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-10% 0px" });

    return (
        <div ref={ref} className={cn("overflow-hidden relative", className)}>
            <motion.div
                initial={{ y: "100%" }}
                animate={isInView ? { y: 0 } : { y: "100%" }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay }}
            >
                {children}
            </motion.div>
        </div>
    );
};

// 2. Highlight Swipe (Dim gray to Brand Color)
export const HighlightSwipe = ({
    children,
    className,
    highlightColor = "text-cyan-400",
    delay = 0.2,
}: {
    children: React.ReactNode;
    className?: string;
    highlightColor?: string;
    delay?: number;
}) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-20% 0px" });

    return (
        <span ref={ref} className={cn("inline-block relative text-gray-600 transition-colors duration-700", className)}>
            <motion.span
                initial={{ opacity: 0, backgroundPosition: "-100% 0" }}
                animate={isInView ? { opacity: 1, backgroundPosition: "200% 0" } : {}}
                transition={{ duration: 1.5, ease: "easeOut", delay }}
                className={cn("absolute inset-0 bg-clip-text text-transparent bg-gradient-to-r from-transparent via-white to-transparent bg-[length:50%_100%] bg-no-repeat", highlightColor)}
            />
            <motion.span
                initial={{ color: "rgb(75 85 99)" }} // gray-600
                animate={isInView ? { color: "var(--target-color)" } : {}}
                transition={{ duration: 0.5, delay: delay + 0.3 }}
                style={{ "--target-color": highlightColor === "text-cyan-400" ? "#22d3ee" : "#ef4444" } as any}
            >
                {children}
            </motion.span>
        </span>
    );
};

// 3. Data Decode (Scramble Effect)
const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";

export const DataDecode = ({
    text,
    className,
    delay = 0,
}: {
    text: string;
    className?: string;
    delay?: number;
}) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-10% 0px" });
    const [displayText, setDisplayText] = useState(text);
    const [isScrambling, setIsScrambling] = useState(false);

    useEffect(() => {
        if (isInView && !isScrambling) {
            setIsScrambling(true);
            let iteration = 0;
            const interval = setInterval(() => {
                setDisplayText(
                    text
                        .split("")
                        .map((char, index) => {
                            if (index < iteration) {
                                return text[index];
                            }
                            return CHARS[Math.floor(Math.random() * CHARS.length)];
                        })
                        .join("")
                );

                if (iteration >= text.length) {
                    clearInterval(interval);
                    setIsScrambling(false);
                }

                iteration += 1 / 2; // Speed of decoding
            }, 30);

            return () => clearInterval(interval);
        }
    }, [isInView]);

    return (
        <span ref={ref} className={className}>
            {displayText}
        </span>
    );
};
