import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

// Nesting level colors - 12 distinct contrasting colors for deep nesting
const NESTING_COLORS = [
    '#3b82f6', // Level 0 (outermost) - Blue
    '#10b981', // Level 1 - Emerald Green  
    '#f59e0b', // Level 2 - Amber
    '#ef4444', // Level 3 - Red
    '#8b5cf6', // Level 4 - Purple
    '#ec4899', // Level 5 - Pink
    '#06b6d4', // Level 6 - Cyan
    '#84cc16', // Level 7 - Lime
    '#f97316', // Level 8 - Orange
    '#6366f1', // Level 9 - Indigo
    '#14b8a6', // Level 10 - Teal
    '#a855f7', // Level 11+ - Violet
];

// Export colors for use in other components (like packing list)
export const getNestingColor = (level) => {
    return NESTING_COLORS[Math.min(level, NESTING_COLORS.length - 1)];
};

function getColorForNestingLevel(level) {
    return NESTING_COLORS[Math.min(level, NESTING_COLORS.length - 1)];
}

// Extract all pipes from nested bundles with nesting level info and their relative positions
function extractPipesFromBundle(bundle, level = 0, centerY = 0, centerZ = 0) {
    const outerDn = bundle.outer_pipe?.dn_mm || bundle.outer_pipe?.outer_diameter_mm || 200;
    const outerRadius = outerDn / 2;
    
    const pipes = [{
        dn_mm: outerDn,
        inner_diameter_mm: bundle.outer_pipe?.inner_diameter_mm || (outerDn * 0.9),
        code: bundle.outer_pipe?.code || 'Unknown',
        nestingLevel: level,
        relativeY: centerY,
        relativeZ: centerZ,
    }];
    
    // Nested pipes are positioned inside the outer pipe
    const nestedArray = bundle.nested_pipes || [];
    if (nestedArray.length > 0) {
        // For single nested pipe, center it
        // For multiple, distribute them inside
        nestedArray.forEach((nested, i) => {
            const nestedDn = nested.outer_pipe?.dn_mm || nested.outer_pipe?.outer_diameter_mm || 100;
            const nestedRadius = nestedDn / 2;
            
            // Calculate offset for nested pipes inside the outer pipe
            // The nested pipe should fit inside the inner diameter of the outer pipe
            const innerRadius = (bundle.outer_pipe?.inner_diameter_mm || (outerDn * 0.9)) / 2;
            
            // For simplicity, center nested pipes (they're telescoped inside)
            const nestedOffsetY = 0;
            const nestedOffsetZ = 0;
            
            pipes.push(...extractPipesFromBundle(
                nested, 
                level + 1, 
                centerY + nestedOffsetY, 
                centerZ + nestedOffsetZ
            ));
        });
    }
    
    return pipes;
}

// Hexagonal packing algorithm - calculates Y-Z positions for bundles
// FIXED: Validates both height AND width constraints to prevent pipes appearing outside truck boundaries
function calculateHexagonalPositions(bundles, truckWidthMm, truckHeightMm) {
    if (!bundles || bundles.length === 0) return [];
    
    const positions = [];
    const skippedBundles = []; // Track bundles that don't fit
    const floorY = 0; // Floor at Y=0
    
    // Sort bundles by outer diameter descending for better packing
    const sortedBundles = [...bundles].sort(
        (a, b) => (b.outer_pipe?.dn_mm || 0) - (a.outer_pipe?.dn_mm || 0)
    );
    
    // Simple row-based hex packing
    let currentZ = 0;
    let currentY = floorY;
    let rowMaxDiameter = 0;
    let oddRow = false;
    const gap = 20; // 20mm gap between bundles
    
    for (const bundle of sortedBundles) {
        const diameter = bundle.outer_pipe?.dn_mm || 200;
        const radius = diameter / 2;
        
        // Calculate hex offset for odd rows
        const zOffset = oddRow ? radius : 0;
        
        // Calculate the FINAL Z position including offset
        const bundleCenterZ_raw = currentZ + radius + zOffset;
        const bundleRightEdge = bundleCenterZ_raw + radius;
        
        // WIDTH CONSTRAINT CHECK: Check if fits in current row
        // Must check AFTER calculating offset to ensure pipe doesn't exceed truck width
        if (bundleRightEdge > truckWidthMm) {
            // Move to next row
            currentZ = 0;
            currentY += rowMaxDiameter * 0.866; // hex row spacing = diameter * sqrt(3)/2
            oddRow = !oddRow;
            rowMaxDiameter = 0;
            
            // Recalculate with new row's offset
            const newZOffset = oddRow ? radius : 0;
            const newBundleCenterZ_raw = currentZ + radius + newZOffset;
            const newBundleRightEdge = newBundleCenterZ_raw + radius;
            
            // If still doesn't fit even at start of row, skip this bundle
            if (newBundleRightEdge > truckWidthMm) {
                skippedBundles.push(bundle);
                console.warn(`Bundle ${bundle.outer_pipe?.code} (DN${diameter}) too wide for truck`);
                continue;
            }
        }
        
        // Recalculate after potential row change
        const finalZOffset = oddRow ? radius : 0;
        const bundleCenterY = currentY + radius;
        const bundleTopY = bundleCenterY + radius;
        
        // HEIGHT CONSTRAINT CHECK: Skip bundle if it would exceed truck height
        if (bundleTopY > truckHeightMm) {
            skippedBundles.push(bundle);
            continue;
        }
        
        // Calculate final centered Z position (centered on truck width)
        const bundleCenterZ = currentZ + radius + finalZOffset - truckWidthMm / 2;
        
        // Final validation: ensure pipe stays within truck bounds on both sides
        const leftEdge = bundleCenterZ - radius;
        const rightEdge = bundleCenterZ + radius;
        const truckHalfWidth = truckWidthMm / 2;
        
        if (leftEdge < -truckHalfWidth || rightEdge > truckHalfWidth) {
            skippedBundles.push(bundle);
            console.warn(`Bundle ${bundle.outer_pipe?.code} would exceed truck width bounds`);
            continue;
        }
        
        positions.push({
            bundle,
            x: 0, // X is along pipe length (centered)
            y: bundleCenterY,
            z: bundleCenterZ, // Center on Z axis
            radius,
            diameter,
            pipes: extractPipesFromBundle(bundle, 0, 0, 0), // Extract with relative positions
            fitsInTruck: true
        });
        
        currentZ += diameter + gap;
        rowMaxDiameter = Math.max(rowMaxDiameter, diameter);
    }
    
    // Log skipped bundles for debugging
    if (skippedBundles.length > 0) {
        console.warn(`TruckView3D: ${skippedBundles.length} bundles skipped due to size constraints`);
    }
    
    return positions;
}

// Hollow pipe component - renders tube with visible wall thickness
// Uses outer cylinder + inner cylinder (darker) to show wall thickness
function HollowPipe({ position, outerRadius, innerRadius, length, nestingLevel, scale }) {
    const color = getColorForNestingLevel(nestingLevel);
    const wallThickness = outerRadius - innerRadius;
    
    // For very thin walls, use simplified rendering
    const hasMeaningfulWall = wallThickness > 1; // At least 1mm wall
    
    return (
        <group position={position} rotation={[0, 0, Math.PI / 2]}>
            {/* Outer surface of pipe */}
            <mesh renderOrder={nestingLevel}>
                <cylinderGeometry args={[
                    outerRadius * scale,  // radiusTop
                    outerRadius * scale,  // radiusBottom
                    length * scale,       // height
                    32,                   // radialSegments
                    1,                    // heightSegments
                    true                  // openEnded - show as tube
                ]} />
                <meshStandardMaterial
                    color={color}
                    roughness={0.4}
                    metalness={0.1}
                    transparent={true}
                    opacity={0.9}
                    side={THREE.FrontSide}
                />
            </mesh>
            
            {/* Inner surface of pipe (darker to show depth) */}
            {hasMeaningfulWall && (
                <mesh renderOrder={nestingLevel + 0.1}>
                    <cylinderGeometry args={[
                        innerRadius * scale,
                        innerRadius * scale,
                        length * scale,
                        32, 1, true
                    ]} />
                    <meshStandardMaterial
                        color={color}
                        roughness={0.6}
                        metalness={0.05}
                        transparent={true}
                        opacity={0.7}
                        side={THREE.BackSide}
                    />
                </mesh>
            )}
            
            {/* End caps (ring geometry to show wall thickness) */}
            {hasMeaningfulWall && (
                <>
                    {/* Front end cap */}
                    <mesh 
                        position={[0, (length * scale) / 2, 0]} 
                        rotation={[Math.PI / 2, 0, 0]}
                        renderOrder={nestingLevel + 0.2}
                    >
                        <ringGeometry args={[
                            innerRadius * scale,  // innerRadius
                            outerRadius * scale,  // outerRadius
                            32                    // segments
                        ]} />
                        <meshStandardMaterial
                            color={color}
                            roughness={0.5}
                            transparent={true}
                            opacity={0.95}
                        />
                    </mesh>
                    {/* Back end cap */}
                    <mesh 
                        position={[0, -(length * scale) / 2, 0]} 
                        rotation={[-Math.PI / 2, 0, 0]}
                        renderOrder={nestingLevel + 0.2}
                    >
                        <ringGeometry args={[
                            innerRadius * scale,
                            outerRadius * scale,
                            32
                        ]} />
                        <meshStandardMaterial
                            color={color}
                            roughness={0.5}
                            transparent={true}
                            opacity={0.95}
                        />
                    </mesh>
                </>
            )}
        </group>
    );
}

// Gap visualization - transparent ring between nested pipes
function NestingGap({ position, outerRadius, innerRadius, length, scale }) {
    // Only render if there's a meaningful gap
    const gapSize = outerRadius - innerRadius;
    if (gapSize < 2) return null; // Less than 2mm gap, don't render
    
    return (
        <group position={position} rotation={[0, 0, Math.PI / 2]}>
            {/* Transparent cylinder showing the gap */}
            <mesh>
                <cylinderGeometry args={[
                    outerRadius * scale,
                    outerRadius * scale,
                    length * scale * 0.99, // Slightly shorter to avoid z-fighting
                    32, 1, true
                ]} />
                <meshStandardMaterial
                    color="#ffffff"
                    roughness={0.3}
                    transparent={true}
                    opacity={0.15}
                    side={THREE.DoubleSide}
                    depthWrite={false}
                />
            </mesh>
            <mesh>
                <cylinderGeometry args={[
                    innerRadius * scale,
                    innerRadius * scale,
                    length * scale * 0.99,
                    32, 1, true
                ]} />
                <meshStandardMaterial
                    color="#ffffff"
                    roughness={0.3}
                    transparent={true}
                    opacity={0.15}
                    side={THREE.DoubleSide}
                    depthWrite={false}
                />
            </mesh>
        </group>
    );
}

// Render all pipes for a bundle position with gaps
function BundlePipes({ bundlePosition, pipeLength, scale }) {
    const { y: bundleY, z: bundleZ, pipes } = bundlePosition;
    
    // Calculate gaps between nesting levels
    const gaps = useMemo(() => {
        const gapList = [];
        // Sort pipes by nesting level to find adjacent levels
        const sortedPipes = [...pipes].sort((a, b) => a.nestingLevel - b.nestingLevel);
        
        for (let i = 0; i < sortedPipes.length - 1; i++) {
            const outerPipe = sortedPipes[i];
            const innerPipe = sortedPipes[i + 1];
            
            // Only show gap if they are adjacent nesting levels
            if (innerPipe.nestingLevel === outerPipe.nestingLevel + 1) {
                const outerInnerRadius = outerPipe.inner_diameter_mm / 2; // Inner diameter of outer pipe
                const innerOuterRadius = innerPipe.dn_mm / 2; // Outer diameter of inner pipe
                
                // Gap exists between outer's inner surface and inner's outer surface
                if (outerInnerRadius > innerOuterRadius) {
                    gapList.push({
                        outerRadius: outerInnerRadius,
                        innerRadius: innerOuterRadius,
                        relativeY: outerPipe.relativeY,
                        relativeZ: outerPipe.relativeZ,
                        level: outerPipe.nestingLevel
                    });
                }
            }
        }
        return gapList;
    }, [pipes]);
    
    return (
        <group>
            {/* Render hollow pipes */}
            {pipes.map((pipe, index) => (
                <HollowPipe
                    key={`pipe-${bundlePosition.bundle?.outer_pipe?.code}-${index}`}
                    position={[
                        0, // X centered (pipe extends along X)
                        (bundleY + pipe.relativeY) * scale, // Y position
                        (bundleZ + pipe.relativeZ) * scale  // Z position
                    ]}
                    outerRadius={pipe.dn_mm / 2}
                    innerRadius={pipe.inner_diameter_mm / 2}
                    length={pipeLength}
                    nestingLevel={pipe.nestingLevel}
                    scale={scale}
                />
            ))}
            
            {/* Render gaps between nested pipes */}
            {gaps.map((gap, index) => (
                <NestingGap
                    key={`gap-${bundlePosition.bundle?.outer_pipe?.code}-${index}`}
                    position={[
                        0,
                        (bundleY + gap.relativeY) * scale,
                        (bundleZ + gap.relativeZ) * scale
                    ]}
                    outerRadius={gap.outerRadius}
                    innerRadius={gap.innerRadius}
                    length={pipeLength}
                    scale={scale}
                />
            ))}
        </group>
    );
}

// Render all pipes
function AllPipes({ pipeData, pipeLength, scale }) {
    return (
        <group>
            {pipeData.map((bundlePos, index) => (
                <BundlePipes
                    key={`bundle-${index}`}
                    bundlePosition={bundlePos}
                    pipeLength={pipeLength}
                    scale={scale}
                />
            ))}
        </group>
    );
}

// Truck container outline - floor at Y=0, container extends upward
function TruckContainer({ lengthMm, widthMm, heightMm, scale }) {
    const l = lengthMm * scale;
    const w = widthMm * scale;
    const h = heightMm * scale;
    
    return (
        <group>
            {/* Floor at Y=0 */}
            <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <planeGeometry args={[l, w]} />
                <meshStandardMaterial color="#444" />
            </mesh>

            {/* Wireframe Box for bounds - centered at h/2 so bottom is at Y=0 */}
            <group position={[0, h / 2, 0]}>
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(l, h, w)]} />
                    <lineBasicMaterial color="#ef4444" linewidth={2} />
                </lineSegments>
                
                {/* Semi-transparent walls */}
                <mesh>
                    <boxGeometry args={[l, h, w]} />
                    <meshStandardMaterial 
                        color="#888" 
                        transparent 
                        opacity={0.05} 
                        side={THREE.BackSide}
                    />
                </mesh>
            </group>
        </group>
    );
}

// Legend component
function NestingLegend() {
    return (
        <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-slate-800/90 rounded-lg p-3 shadow-lg text-xs">
            <div className="font-semibold mb-2">Nesting Levels</div>
            {NESTING_COLORS.map((color, i) => (
                <div key={i} className="flex items-center gap-2 mb-1">
                    <div 
                        className="w-4 h-4 rounded" 
                        style={{ backgroundColor: color, opacity: i > 0 ? 0.7 : 1 }}
                    />
                    <span>Level {i}{i === 0 ? ' (Outer)' : i === NESTING_COLORS.length - 1 ? '+' : ''}</span>
                </div>
            ))}
        </div>
    );
}

// Stats overlay
function StatsOverlay({ bundleCount, pipeCount, weightKg }) {
    return (
        <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-800/90 rounded-lg p-3 shadow-lg text-xs">
            <div className="font-semibold mb-1">Truck Load</div>
            <div>{bundleCount} bundles</div>
            <div>{pipeCount} total pipes</div>
            <div>{(weightKg || 0).toLocaleString()} kg</div>
        </div>
    );
}

export default function TruckView3D({
    loadingPlan,
    truckConfig = { 
        lengthMm: 13600, 
        widthMm: 2480, 
        heightMm: 2700,
        pipeLengthM: 12
    }
}) {
    // Convert old config format if needed
    const config = {
        lengthMm: truckConfig.lengthMm || truckConfig.length * 1000 || 13600,
        widthMm: truckConfig.widthMm || truckConfig.width * 1000 || 2480,
        heightMm: truckConfig.heightMm || truckConfig.height * 1000 || 2700,
        pipeLengthM: truckConfig.pipeLengthM || truckConfig.pipeLength || 12
    };
    
    // Scale factor: convert mm to scene units (1 unit = 1000mm = 1m for reasonable camera distance)
    const scale = 1 / 1000;
    
    // Calculate bundle positions using hexagonal packing
    const bundlePositions = useMemo(() => {
        if (!loadingPlan?.bundles?.length) return [];
        return calculateHexagonalPositions(
            loadingPlan.bundles,
            config.widthMm,
            config.heightMm
        );
    }, [loadingPlan?.bundles, config.widthMm, config.heightMm]);
    
    // Count total pipes for stats
    const totalPipes = useMemo(() => {
        return bundlePositions.reduce((sum, pos) => sum + pos.pipes.length, 0);
    }, [bundlePositions]);
    
    const isEmpty = !loadingPlan?.bundles?.length;
    
    return (
        <div className="h-[500px] w-full bg-gradient-to-b from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 rounded-lg border overflow-hidden relative">
            <Canvas shadows>
                <PerspectiveCamera 
                    makeDefault 
                    position={[config.lengthMm * scale * 0.8, config.heightMm * scale * 1.5, config.widthMm * scale * 2]} 
                    fov={50}
                />
                <OrbitControls 
                    enablePan={true}
                    enableZoom={true}
                    minDistance={2}
                    maxDistance={50}
                    target={[0, config.heightMm * scale / 2, 0]}
                />
                
                {/* Lighting */}
                <ambientLight intensity={0.6} />
                <directionalLight 
                    position={[10, 15, 10]} 
                    intensity={1} 
                    castShadow 
                    shadow-mapSize={[2048, 2048]}
                />
                <directionalLight position={[-5, 5, -5]} intensity={0.3} />

                {/* Truck container */}
                <TruckContainer 
                    lengthMm={config.lengthMm}
                    widthMm={config.widthMm}
                    heightMm={config.heightMm}
                    scale={scale}
                />

                {/* Render all pipes */}
                {!isEmpty && (
                    <AllPipes 
                        pipeData={bundlePositions}
                        pipeLength={config.pipeLengthM * 1000} // Convert to mm
                        scale={scale}
                    />
                )}
                
                {isEmpty && (
                    <mesh position={[0, config.heightMm * scale / 2, 0]}>
                        <boxGeometry args={[0.5, 0.5, 0.5]} />
                        <meshStandardMaterial color="#ccc" transparent opacity={0.3} />
                    </mesh>
                )}

                <ContactShadows 
                    opacity={0.4} 
                    scale={20} 
                    blur={2} 
                    far={15} 
                    resolution={256} 
                    color="#000000"
                    position={[0, -0.01, 0]}
                />
                <Environment preset="city" />
            </Canvas>
            
            {/* Overlays */}
            <NestingLegend />
            {!isEmpty && (
                <StatsOverlay 
                    bundleCount={loadingPlan?.bundles?.length || 0}
                    pipeCount={totalPipes}
                    weightKg={loadingPlan?.current_payload_kg || loadingPlan?.total_weight_kg}
                />
            )}
            
            {/* Empty state message */}
            {isEmpty && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="bg-white/80 dark:bg-slate-800/80 rounded-lg px-4 py-2 text-muted-foreground">
                        No bundles to display
                    </div>
                </div>
            )}
        </div>
    );
}
