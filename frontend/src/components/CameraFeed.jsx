import React, { useRef, useEffect, useState } from 'react';
import { websocketService } from '../services/websocket';

const CameraFeed = ({ isActive, onPoseUpdate }) => {
  const canvasRef = useRef(null);
  const [landmarks, setLandmarks] = useState([]);
  const [fps, setFps] = useState(0);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(Date.now());

  useEffect(() => {
    if (!isActive) return;

    const handlePoseData = (data) => {
      if (data.type === 'pose_update' && data.data) {
        const newLandmarks = data.data.landmarks || [];
        setLandmarks(newLandmarks);
        
        if (onPoseUpdate) {
          onPoseUpdate(newLandmarks);
        }

        // Calculate FPS
        frameCountRef.current++;
        const now = Date.now();
        const elapsed = now - lastTimeRef.current;
        
        if (elapsed >= 1000) {
          setFps(Math.round((frameCountRef.current * 1000) / elapsed));
          frameCountRef.current = 0;
          lastTimeRef.current = now;
        }

        // Draw landmarks on canvas
        drawLandmarks(newLandmarks);
      }
    };

    websocketService.addListener(handlePoseData);

    return () => {
      websocketService.removeListener(handlePoseData);
    };
  }, [isActive, onPoseUpdate]);

  const drawLandmarks = (landmarks) => {
    const canvas = canvasRef.current;
    if (!canvas || !landmarks || landmarks.length === 0) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw connections
    const connections = [
      // Face
      [0, 1], [1, 2], [2, 3], [3, 7],
      [0, 4], [4, 5], [5, 6], [6, 8],
      [9, 10],
      
      // Torso
      [11, 12], [11, 23], [12, 24], [23, 24],
      
      // Left arm
      [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
      [17, 19],
      
      // Right arm
      [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
      [18, 20],
      
      // Left leg
      [23, 25], [25, 27], [27, 29], [27, 31], [29, 31],
      
      // Right leg
      [24, 26], [26, 28], [28, 30], [28, 32], [30, 32]
    ];

    // Draw connections
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    
    connections.forEach(([start, end]) => {
      if (start < landmarks.length && end < landmarks.length) {
        const startLm = landmarks[start];
        const endLm = landmarks[end];
        
        ctx.beginPath();
        ctx.moveTo(startLm.x * width, startLm.y * height);
        ctx.lineTo(endLm.x * width, endLm.y * height);
        ctx.stroke();
      }
    });

    // Draw landmarks
    ctx.fillStyle = '#ff0000';
    landmarks.forEach((lm) => {
      const x = lm.x * width;
      const y = lm.y * height;
      
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  return (
    <div className="camera-feed">
      <div className="feed-header">
        <h3>Camera Feed</h3>
        <div className="fps-counter">FPS: {fps}</div>
      </div>
      <div className="canvas-container">
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          style={{
            border: '2px solid #333',
            borderRadius: '8px',
            backgroundColor: '#000'
          }}
        />
        {!isActive && (
          <div className="overlay">
            <p>Camera Inactive</p>
            <p style={{ fontSize: '14px', opacity: 0.7 }}>
              Start the camera to begin pose detection
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraFeed;
