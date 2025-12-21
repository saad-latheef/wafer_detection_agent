"use client";

import { useEffect, useRef } from "react";

export default function OrbitalSystem() {
    return (
        <div className="relative h-[500px] w-full flex items-center justify-center font-mono">
            <svg
                className="w-full h-full"
                viewBox="0 0 600 500"
                xmlns="http://www.w3.org/2000/svg"
            >
                {/* Definitions for Glows */}
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.1" />
                        <stop offset="50%" stopColor="#00d4ff" stopOpacity="0.8" />
                        <stop offset="100%" stopColor="#00d4ff" stopOpacity="0.1" />
                    </linearGradient>
                </defs>

                {/* Central Orbit Ring (Dotted) */}
                <ellipse
                    cx="300"
                    cy="250"
                    rx="180"
                    ry="180"
                    fill="none"
                    stroke="#00d4ff"
                    strokeWidth="1"
                    strokeDasharray="4,4"
                    opacity="0.3"
                    className="animate-spin-slow"
                    style={{ transformOrigin: "center" }}
                />

                {/* Connection Lines (Bezier Paths) */}
                {/* Top to Center */}
                <path d="M 300 110 L 300 190" stroke="#00d4ff" strokeWidth="1" opacity="0.3" />
                {/* Center to Right */}
                <path d="M 360 250 L 460 250" stroke="#00d4ff" strokeWidth="1" opacity="0.3" />
                {/* Center to Bottom */}
                <path d="M 300 310 L 300 390" stroke="#00d4ff" strokeWidth="1" opacity="0.3" />
                {/* Left to Center */}
                <path d="M 140 250 L 240 250" stroke="#00d4ff" strokeWidth="1" opacity="0.3" />

                {/* Animated Data Packets (Pulses) */}
                {/* Top Input -> Master */}
                <circle r="3" fill="#ffffff" filter="url(#glow)">
                    <animateMotion dur="2s" repeatCount="indefinite" path="M 300 110 L 300 190" />
                </circle>
                {/* Master -> Right Detection */}
                <circle r="3" fill="#ffffff" filter="url(#glow)">
                    <animateMotion dur="2s" begin="0.5s" repeatCount="indefinite" path="M 360 250 L 460 250" />
                </circle>
                {/* Master -> Bottom Confidence */}
                <circle r="3" fill="#ffffff" filter="url(#glow)">
                    <animateMotion dur="2s" begin="1s" repeatCount="indefinite" path="M 300 310 L 300 390" />
                </circle>
                {/* Left Insight -> Master */}
                <circle r="3" fill="#ffffff" filter="url(#glow)">
                    <animateMotion dur="2s" begin="1.5s" repeatCount="indefinite" path="M 140 250 L 240 250" />
                </circle>

                {/* Master Agent (Center) */}
                <g className="animate-pulse-slow">
                    {/* Outer Rings */}
                    <circle cx="300" cy="250" r="60" fill="none" stroke="#00d4ff" strokeWidth="1" opacity="0.5" />
                    <circle cx="300" cy="250" r="50" fill="none" stroke="#00d4ff" strokeWidth="2" />

                    {/* Inner Core */}
                    <circle cx="300" cy="250" r="20" fill="#00d4ff" opacity="0.2" />
                    <circle cx="300" cy="250" r="5" fill="#ffffff" filter="url(#glow)" />

                    {/* Label */}
                    <text x="300" y="335" textAnchor="middle" fill="#00d4ff" fontSize="12" letterSpacing="2">MASTER_NODE</text>
                </g>

                {/* Sub-agents (Nodes) */}
                <g>
                    {/* Top: Ingestion */}
                    <g transform="translate(265, 40)">
                        <rect width="70" height="70" fill="rgba(0, 212, 255, 0.05)" stroke="#00d4ff" strokeWidth="1" />
                        <rect x="2" y="2" width="66" height="66" fill="none" stroke="#00d4ff" strokeWidth="1" strokeDasharray="2,2" opacity="0.5" />
                        <text x="35" y="40" textAnchor="middle" fill="#ffffff" fontSize="20">IN</text>
                        <text x="35" y="85" textAnchor="middle" fill="#00d4ff" fontSize="10">INGESTION</text>
                    </g>

                    {/* Right: Detection */}
                    <g transform="translate(460, 215)">
                        <rect width="70" height="70" fill="rgba(0, 212, 255, 0.05)" stroke="#00d4ff" strokeWidth="1" />
                        <text x="35" y="40" textAnchor="middle" fill="#ffffff" fontSize="20">ML</text>
                        <text x="35" y="85" textAnchor="middle" fill="#00d4ff" fontSize="10">DETECTOR</text>
                    </g>

                    {/* Bottom: Analysis */}
                    <g transform="translate(265, 390)">
                        <rect width="70" height="70" fill="rgba(0, 212, 255, 0.05)" stroke="#00d4ff" strokeWidth="1" />
                        <text x="35" y="40" textAnchor="middle" fill="#ffffff" fontSize="20">AN</text>
                        <text x="35" y="85" textAnchor="middle" fill="#00d4ff" fontSize="10">ANALYZER</text>
                    </g>

                    {/* Left: Insight */}
                    <g transform="translate(70, 215)">
                        <rect width="70" height="70" fill="rgba(0, 212, 255, 0.05)" stroke="#00d4ff" strokeWidth="1" />
                        <text x="35" y="40" textAnchor="middle" fill="#ffffff" fontSize="20">OUT</text>
                        <text x="35" y="85" textAnchor="middle" fill="#00d4ff" fontSize="10">INSIGHT</text>
                    </g>
                </g>
            </svg>
        </div>
    );
}

