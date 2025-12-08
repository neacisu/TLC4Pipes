import React, { useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

// Component to render a single pipe (cylinder)
function Pipe3D({ x, y, z, diameter, length, color, isHollow }) {
    return (
        <group position={[x, y, z]}>
            <mesh rotation={[0, 0, Math.PI / 2]}>
                <cylinderGeometry args={[diameter / 2, diameter / 2, length, 32]} />
                <meshStandardMaterial
                    color={color}
                    roughness={0.3}
                    metalness={0.1}
                    transparent={true}
                    opacity={0.9}
                />
            </mesh>
            {/* Outline for better visibility */}
            <mesh rotation={[0, 0, Math.PI / 2]}>
                <cylinderGeometry args={[diameter / 2, diameter / 2, length, 32]} />
                <meshBasicMaterial wireframe color="black" transparent opacity={0.1} />
            </mesh>
        </group>
    );
}

// Component to render the truck cargo space outline
function TruckContainer({ length, width, height }) {
    return (
        <group>
            {/* Floor */}
            <mesh position={[0, -height / 2 - 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <planeGeometry args={[length, width]} />
                <meshStandardMaterial color="#333" />
            </mesh>

            {/* Wireframe Box for bounds */}
            <lineSegments>
                <edgesGeometry args={[new THREE.BoxGeometry(length, height, width)]} />
                <lineBasicMaterial color="red" dashSize={0.5} gapSize={0.2} />
            </lineSegments>
        </group>
    );
}

export default function TruckView3D({
    loadingPlan,
    truckConfig = { length: 13.6, width: 2.48, height: 2.7 }
}) {
    if (!loadingPlan) return null;

    // Convert API response plan to renderable items
    // Assuming loadingPlan follows the structure returned by backend
    // Since backend isn't actually running 3D packing yet, we might simulate or visualize 
    // based on available coordinates if they exist. 
    // FOR DEMO/MOCK: We render a simple stack if no coords provided.

    return (
        <div className="h-[500px] w-full bg-slate-100 rounded-lg border overflow-hidden">
            <Canvas shadows>
                <PerspectiveCamera makeDefault position={[10, 5, 10]} />
                <OrbitControls />
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
                <Environment preset="city" />

                <group position={[0, 0, 0]}>
                    <TruckContainer
                        length={truckConfig.length}
                        width={truckConfig.width}
                        height={truckConfig.height}
                    />

                    {/* Render Pipes */}
                    {/* Placeholder stacking logic for demo visualization until real coords come from backend */}
                    <Pipe3D x={0} y={-truckConfig.height / 2 + 0.5} z={0} diameter={1.0} length={12} color="#3b82f6" />
                    <Pipe3D x={0} y={-truckConfig.height / 2 + 0.5} z={1} diameter={0.5} length={12} color="#10b981" />
                    <Pipe3D x={0} y={-truckConfig.height / 2 + 0.5} z={-1} diameter={0.5} length={12} color="#10b981" />

                </group>
                <ContactShadows opacity={0.5} scale={10} blur={1} far={10} resolution={256} color="#000000" />
            </Canvas>
        </div>
    );
}
