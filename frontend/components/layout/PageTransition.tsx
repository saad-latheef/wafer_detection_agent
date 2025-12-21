"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface PageTransitionProps {
    children: ReactNode;
    className?: string;
}

export const PageTransition = ({ children, className }: PageTransitionProps) => {
    return (
        <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{
                duration: 0.3,
                ease: [0.25, 0.1, 0.25, 1], // Custom ease-out curve
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
};
