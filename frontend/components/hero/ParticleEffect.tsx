"use client";

import { useEffect, useRef, useState } from "react";

interface Particle {
    x: number;
    y: number;
    baseVx: number;
    baseVy: number;
    pushVx: number;
    pushVy: number;
    radius: number;
}

export default function ParticleEffect() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const mouseRef = useRef({ x: -1000, y: -1000 });

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Set canvas size
        const updateSize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        updateSize();
        window.addEventListener("resize", updateSize);

        // Track mouse position
        const handleMouseMove = (e: MouseEvent) => {
            mouseRef.current = { x: e.clientX, y: e.clientY };
        };
        const handleMouseLeave = () => {
            mouseRef.current = { x: -1000, y: -1000 };
        };
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseleave", handleMouseLeave);

        // Particle system with active drift
        const particles: Particle[] = [];
        const particleCount = 150;

        for (let i = 0; i < particleCount; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            // Base drift speed (constant)
            const speed = 0.2 + Math.random() * 0.3; // Slower, smoother drift
            const angle = Math.random() * Math.PI * 2;

            particles.push({
                x,
                y,
                baseVx: Math.cos(angle) * speed,
                baseVy: Math.sin(angle) * speed,
                pushVx: 0,
                pushVy: 0,
                radius: Math.random() * 1.5 + 0.5,
            });
        }

        // Animation loop
        const animate = () => {
            ctx.fillStyle = "rgba(10, 15, 26, 0.2)"; // Clear with trails (0.2 opacity)
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const mouse = mouseRef.current;

            particles.forEach((particle) => {
                // Calculate distance to mouse
                const dx = mouse.x - particle.x;
                const dy = mouse.y - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const maxDistance = 200;

                // Mouse interaction: repulsion
                if (distance < maxDistance) {
                    const force = (maxDistance - distance) / maxDistance;
                    const angle = Math.atan2(dy, dx);
                    const pushStrength = 0.35; // Reduced push strength

                    // Add to push velocity (repel)
                    particle.pushVx -= Math.cos(angle) * force * pushStrength;
                    particle.pushVy -= Math.sin(angle) * force * pushStrength;
                }

                // Decay push velocity (friction)
                particle.pushVx *= 0.96;
                particle.pushVy *= 0.96;

                // Move particle (Base Drift + Push Force)
                particle.x += particle.baseVx + particle.pushVx;
                particle.y += particle.baseVy + particle.pushVy;

                // Wrap around edges
                if (particle.x < 0) particle.x = canvas.width;
                if (particle.x > canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = canvas.height;
                if (particle.y > canvas.height) particle.y = 0;

                // Draw particle
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                ctx.fillStyle = "rgba(0, 212, 255, 0.8)";
                ctx.fill();

                // Draw glow
                const gradient = ctx.createRadialGradient(
                    particle.x,
                    particle.y,
                    0,
                    particle.x,
                    particle.y,
                    particle.radius * 4
                );
                gradient.addColorStop(0, "rgba(0, 212, 255, 0.4)");
                gradient.addColorStop(1, "rgba(0, 212, 255, 0)");
                ctx.fillStyle = gradient;
                ctx.fillRect(
                    particle.x - particle.radius * 4,
                    particle.y - particle.radius * 4,
                    particle.radius * 8,
                    particle.radius * 8
                );
            });

            // Draw constellation connections (neural network effect)
            const connectionDistance = 150;
            ctx.strokeStyle = "rgba(0, 212, 255, 0.15)";
            ctx.lineWidth = 0.5;

            // Optimization: Grid-based or just limit checks? 
            // For 150 particles, N^2 (22500) is fine for modern desktops.
            for (let i = 0; i < particles.length; i++) {
                // Check neighbors
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;

                    // Quick optimization
                    if (Math.abs(dx) > connectionDistance || Math.abs(dy) > connectionDistance) continue;

                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < connectionDistance) {
                        const opacity = (1 - distance / connectionDistance) * 0.3;
                        ctx.strokeStyle = `rgba(0, 212, 255, ${opacity})`;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }

            requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener("resize", updateSize);
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseleave", handleMouseLeave);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 pointer-events-none opacity-50"
        />
    );
}
