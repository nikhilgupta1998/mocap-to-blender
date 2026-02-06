import React, { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import * as THREE from 'three';

// Skeleton component that renders bones
const Skeleton = ({ landmarks }) => {
  const linesRef = useRef();
  const pointsRef = useRef();

  useEffect(() => {
    if (!landmarks || landmarks.length === 0) return;

    // Define connections between landmarks
    const connections = [
      // Torso
      [11, 12], [11, 23], [12, 24], [23, 24],
      
      // Left arm
      [11, 13], [13, 15],
      
      // Right arm
      [12, 14], [14, 16],
      
      // Left leg
      [23, 25], [25, 27],
      
      // Right leg
      [24, 26], [26, 28],
      
      // Head
      [0, 11], [0, 12]
    ];

    // Create line geometry
    const positions = [];
    connections.forEach(([start, end]) => {
      if (start < landmarks.length && end < landmarks.length) {
        const startLm = landmarks[start];
        const endLm = landmarks[end];
        
        // Convert from MediaPipe coordinates to 3D space
        positions.push(
          (startLm.x - 0.5) * 2, startLm.y * -2, startLm.z * -2,
          (endLm.x - 0.5) * 2, endLm.y * -2, endLm.z * -2
        );
      }
    });

    if (linesRef.current) {
      linesRef.current.geometry.setAttribute(
        'position',
        new THREE.Float32BufferAttribute(positions, 3)
      );
    }

    // Create points for landmarks
    const pointPositions = landmarks.map(lm => [
      (lm.x - 0.5) * 2,
      lm.y * -2,
      lm.z * -2
    ]).flat();

    if (pointsRef.current) {
      pointsRef.current.geometry.setAttribute(
        'position',
        new THREE.Float32BufferAttribute(pointPositions, 3)
      );
    }
  }, [landmarks]);

  return (
    <group>
      {/* Lines connecting landmarks */}
      <lineSegments ref={linesRef}>
        <bufferGeometry />
        <lineBasicMaterial color="#00ff00" linewidth={2} />
      </lineSegments>
      
      {/* Points for landmarks */}
      <points ref={pointsRef}>
        <bufferGeometry />
        <pointsMaterial size={0.05} color="#ff0000" />
      </points>
    </group>
  );
};

const SkeletonPreview = ({ landmarks }) => {
  return (
    <div className="skeleton-preview">
      <h3>3D Preview</h3>
      <div style={{ width: '100%', height: '500px', backgroundColor: '#1a1a1a', borderRadius: '8px' }}>
        <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          
          {/* Grid helper */}
          <Grid
            args={[10, 10]}
            cellColor="#444444"
            sectionColor="#666666"
            position={[0, -2, 0]}
          />
          
          {/* Skeleton */}
          <Skeleton landmarks={landmarks} />
          
          {/* Camera controls */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
          />
        </Canvas>
      </div>
      <div className="preview-info">
        {landmarks && landmarks.length > 0 ? (
          <p>Tracking {landmarks.length} landmarks</p>
        ) : (
          <p>No pose detected</p>
        )}
      </div>
    </div>
  );
};

export default SkeletonPreview;
