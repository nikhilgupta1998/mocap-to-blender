"""
Recording system for managing motion capture sessions.
"""
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class RecordingFrame(BaseModel):
    """Single frame in a recording."""
    frame_id: int
    timestamp: float
    landmarks: List[Dict[str, float]]
    world_landmarks: Optional[List[Dict[str, float]]] = None


class RecordingMetadata(BaseModel):
    """Metadata for a recording session."""
    session_id: str
    fps: float
    duration: float
    frame_count: int
    timestamp: str
    landmark_count: int = 33


class Recording(BaseModel):
    """Complete recording session."""
    metadata: RecordingMetadata
    frames: List[RecordingFrame]


class RecordingManager:
    """Manages recording sessions and data storage."""
    
    def __init__(self, recordings_dir: str = "recordings"):
        """
        Initialize the recording manager.
        
        Args:
            recordings_dir: Directory to store recordings
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)
        
        self.current_session_id: Optional[str] = None
        self.current_frames: List[RecordingFrame] = []
        self.recording_start_time: Optional[float] = None
        self.target_fps: float = 30.0
    
    def start_recording(self, fps: float = 30.0) -> str:
        """
        Start a new recording session.
        
        Args:
            fps: Target frames per second
            
        Returns:
            Session ID
        """
        self.current_session_id = str(uuid.uuid4())
        self.current_frames = []
        self.recording_start_time = time.time()
        self.target_fps = fps
        
        return self.current_session_id
    
    def add_frame(
        self,
        landmarks: List[Dict[str, float]],
        world_landmarks: Optional[List[Dict[str, float]]] = None
    ) -> int:
        """
        Add a frame to the current recording.
        
        Args:
            landmarks: Pose landmarks for this frame
            world_landmarks: World coordinates (optional)
            
        Returns:
            Frame ID
        """
        if self.current_session_id is None:
            raise ValueError("No active recording session")
        
        frame_id = len(self.current_frames)
        timestamp = time.time() - self.recording_start_time
        
        frame = RecordingFrame(
            frame_id=frame_id,
            timestamp=timestamp,
            landmarks=landmarks,
            world_landmarks=world_landmarks
        )
        
        self.current_frames.append(frame)
        return frame_id
    
    def stop_recording(self) -> Recording:
        """
        Stop the current recording and save it.
        
        Returns:
            Complete recording data
        """
        if self.current_session_id is None:
            raise ValueError("No active recording session")
        
        duration = time.time() - self.recording_start_time
        frame_count = len(self.current_frames)
        
        metadata = RecordingMetadata(
            session_id=self.current_session_id,
            fps=self.target_fps,
            duration=duration,
            frame_count=frame_count,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        
        recording = Recording(
            metadata=metadata,
            frames=self.current_frames
        )
        
        # Save to file
        self._save_recording(recording)
        
        # Reset state
        session_id = self.current_session_id
        self.current_session_id = None
        self.current_frames = []
        self.recording_start_time = None
        
        return recording
    
    def _save_recording(self, recording: Recording) -> None:
        """Save recording to JSON file."""
        file_path = self.recordings_dir / f"{recording.metadata.session_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(recording.dict(), f, indent=2)
    
    def get_recording(self, session_id: str) -> Optional[Recording]:
        """
        Load a recording by session ID.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Recording data or None if not found
        """
        file_path = self.recordings_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return Recording(**data)
    
    def list_recordings(self) -> List[RecordingMetadata]:
        """
        List all available recordings.
        
        Returns:
            List of recording metadata
        """
        recordings = []
        
        for file_path in self.recordings_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    recordings.append(RecordingMetadata(**data['metadata']))
            except Exception as e:
                print(f"Error loading recording {file_path}: {e}")
        
        # Sort by timestamp (newest first)
        recordings.sort(key=lambda r: r.timestamp, reverse=True)
        
        return recordings
    
    def delete_recording(self, session_id: str) -> bool:
        """
        Delete a recording.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.recordings_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        return True
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.current_session_id is not None
