"use client";

import { useEffect, useRef } from "react";

export default function SiliconGrid() {
    const gridRef = useRef<HTMLDivElement>(null);

    return (
        <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none bg-[#050810]">
            {/* Grid Container with perspective/transform if desired, but 2D is safer to start */}
            <div
                ref={gridRef}
                className="absolute inset-0 w-full h-[200%] animate-grid-drift"
                style={{
                    backgroundImage: `
                        linear-gradient(to right, rgba(0, 212, 255, 0.03) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(0, 212, 255, 0.03) 1px, transparent 1px)
                    `,
                    backgroundSize: "60px 60px",
                }}
            />

            {/* Vignette Overlay (Darker edges) */}
            <div
                className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#050810_100%)] opacity-80"
                style={{
                    background: "radial-gradient(circle at 50% 50%, transparent 20%, #050810 100%)"
                }}
            />
        </div>
    );
}
