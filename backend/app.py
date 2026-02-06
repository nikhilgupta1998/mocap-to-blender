"""
FastAPI application for motion capture backend.
"""
import asyncio
import cv2
import numpy as np
import time
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from pose_detector import PoseDetector
from smoother import ExponentialMovingAverage, KalmanFilter
from recording import RecordingManager, RecordingMetadata
from retargeting import BoneRetargeter
from exporters import BVHExporter, BlenderScriptGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Motion Capture API",
    description="Real-time motion capture to Blender animation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
camera = None
pose_detector: Optional[PoseDetector] = None
smoother: Optional[ExponentialMovingAverage] = None
recording_manager = RecordingManager()
retargeter = BoneRetargeter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# Request/Response models
class CameraStartRequest(BaseModel):
    camera_id: int = 0
    smoothing_alpha: float = 0.3


class RecordingStartRequest(BaseModel):
    fps: float = 30.0


class ExportRequest(BaseModel):
    session_id: str
    format: str  # 'bvh', 'fbx', or 'blender'


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "camera_active": camera is not None,
        "recording": recording_manager.is_recording()
    }


@app.post("/api/camera/start")
async def start_camera(request: CameraStartRequest):
    """Start camera feed and pose detection."""
    global camera, pose_detector, smoother
    
    try:
        # Initialize camera
        camera = cv2.VideoCapture(request.camera_id)
        if not camera.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open camera")
        
        # Initialize pose detector
        pose_detector = PoseDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        
        # Initialize smoother
        smoother = ExponentialMovingAverage(alpha=request.smoothing_alpha)
        
        return {
            "status": "started",
            "camera_id": request.camera_id,
            "smoothing_alpha": request.smoothing_alpha
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/camera/stop")
async def stop_camera():
    """Stop camera feed."""
    global camera, pose_detector, smoother
    
    if camera is not None:
        camera.release()
        camera = None
    
    if pose_detector is not None:
        pose_detector.close()
        pose_detector = None
    
    smoother = None
    
    return {"status": "stopped"}


@app.websocket("/ws/pose")
async def websocket_pose(websocket: WebSocket):
    """WebSocket endpoint for real-time pose streaming."""
    await manager.connect(websocket)
    
    try:
        while True:
            if camera is None or pose_detector is None:
                await asyncio.sleep(0.1)
                continue
            
            # Capture frame
            ret, frame = camera.read()
            if not ret:
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to capture frame"
                })
                continue
            
            # Detect pose
            pose_data = pose_detector.detect(frame)
            
            if pose_data:
                landmarks = pose_data['landmarks']
                world_landmarks = pose_data.get('world_landmarks', [])
                
                # Apply smoothing
                if smoother:
                    landmarks = smoother.smooth(landmarks)
                
                # Add to recording if active
                if recording_manager.is_recording():
                    recording_manager.add_frame(landmarks, world_landmarks)
                
                # Send to client
                await websocket.send_json({
                    "type": "pose_update",
                    "data": {
                        "landmarks": landmarks,
                        "world_landmarks": world_landmarks,
                        "timestamp": time.time()
                    }
                })
            
            # Control frame rate
            await asyncio.sleep(1/30)  # ~30 FPS
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/recording/start")
async def start_recording(request: RecordingStartRequest):
    """Start a new recording session."""
    try:
        session_id = recording_manager.start_recording(fps=request.fps)
        return {
            "status": "recording",
            "session_id": session_id,
            "fps": request.fps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recording/stop")
async def stop_recording():
    """Stop the current recording session."""
    try:
        recording = recording_manager.stop_recording()
        return {
            "status": "stopped",
            "session_id": recording.metadata.session_id,
            "frame_count": recording.metadata.frame_count,
            "duration": recording.metadata.duration
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recording/{session_id}")
async def get_recording(session_id: str):
    """Get a specific recording."""
    recording = recording_manager.get_recording(session_id)
    
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return recording


@app.get("/api/recordings", response_model=List[RecordingMetadata])
async def list_recordings():
    """List all recordings."""
    return recording_manager.list_recordings()


@app.delete("/api/recording/{session_id}")
async def delete_recording(session_id: str):
    """Delete a recording."""
    if recording_manager.delete_recording(session_id):
        return {"status": "deleted", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Recording not found")


@app.post("/api/export/bvh")
async def export_bvh(request: ExportRequest):
    """Export recording as BVH file."""
    recording = recording_manager.get_recording(request.session_id)
    
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    try:
        # Create exports directory
        import os
        os.makedirs("exports", exist_ok=True)
        
        output_path = f"exports/{request.session_id}.bvh"
        exporter = BVHExporter()
        exporter.export(recording, output_path)
        
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=f"{request.session_id}.bvh"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/blender")
async def export_blender_script(request: ExportRequest):
    """Export recording as Blender Python script."""
    recording = recording_manager.get_recording(request.session_id)
    
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    try:
        # Create exports directory
        import os
        os.makedirs("exports", exist_ok=True)
        
        output_path = f"exports/{request.session_id}.py"
        generator = BlenderScriptGenerator()
        generator.generate(recording, output_path)
        
        return FileResponse(
            output_path,
            media_type="text/x-python",
            filename=f"{request.session_id}.py"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
