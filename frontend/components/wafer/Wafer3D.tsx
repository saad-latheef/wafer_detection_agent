"use client";

import { useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";

function WaferMesh() {
    const meshRef = useRef<THREE.Mesh>(null);
    const [hovered, setHovered] = useState(false);

    useFrame(() => {
        if (meshRef.current && !hovered) {
            meshRef.current.rotation.z += 0.002;
        }
    });

    // Create grid texture
    const gridSize = 12;
    const defects = [
        { x: 2, y: 3 },
        { x: 7, y: 5 },
        { x: 5, y: 8 },
        { x: 9, y: 7 },
    ];

    return (
        <group ref={meshRef}>
            {/* Main wafer circle */}
            <mesh>
                <circleGeometry args={[3, 64]} />
                <meshBasicMaterial color="#141b2d" />
            </mesh>

            {/* Outer glow ring */}
            <mesh>
                <ringGeometry args={[3, 3.1, 64]} />
                <meshBasicMaterial color="#00d4ff" transparent opacity={0.8} />
            </mesh>

            {/* Grid lines */}
            {Array.from({ length: gridSize + 1 }).map((_, i) => {
                const pos = -3 + (i * 6) / gridSize;
                return (
                    <group key={`grid-${i}`}>
                        {/* Vertical line */}
                        <line>
                            <bufferGeometry>
                                <bufferAttribute
                                    attach="attributes-position"
                                    count={2}
                                    array={new Float32Array([pos, -3, 0, pos, 3, 0])}
                                    itemSize={3}
                                />
                            </bufferGeometry>
                            <lineBasicMaterial color="#00d4ff" opacity={0.2} transparent />
                        </line>
                        {/* Horizontal line */}
                        <line>
                            <bufferGeometry>
                                <bufferAttribute
                                    attach="attributes-position"
                                    count={2}
                                    array={new Float32Array([-3, pos, 0, 3, pos, 0])}
                                    itemSize={3}
                                />
                            </bufferGeometry>
                            <lineBasicMaterial color="#00d4ff" opacity={0.2} transparent />
                        </line>
                    </group>
                );
            })}

            {/* Defect markers */}
            {defects.map((defect, index) => {
                const x = -3 + (defect.x * 6) / gridSize;
                const y = -3 + (defect.y * 6) / gridSize;
                return (
                    <group key={`defect-${index}`} position={[x, y, 0.1]}>
                        <mesh
                            onPointerOver={() => setHovered(true)}
                            onPointerOut={() => setHovered(false)}
                        >
                            <circleGeometry args={[0.15, 32]} />
                            <meshBasicMaterial color="#ff0055" />
                        </mesh>
                        {hovered && (
                            <Html position={[0, 0.3, 0]} center>
                                <div className="bg-background-card px-3 py-2 rounded border border-accent-red text-sm whitespace-nowrap">
                                    <div className="font-semibold text-accent-red">DEFECT</div>
                                    <div className="text-text-secondary text-xs">Manual Handling</div>
                                </div>
                            </Html>
                        )}
                    </group>
                );
            })}
        </group>
    );
}

export default function Wafer3D() {
    return (
        <div className="w-full h-full">
            <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <WaferMesh />
                <OrbitControls enableZoom={false} enablePan={false} />
            </Canvas>
        </div>
    );
}
