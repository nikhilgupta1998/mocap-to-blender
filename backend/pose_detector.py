"""
MediaPipe-based pose detection module for real-time motion capture.
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, List, Dict, Any


class PoseDetector:
    """Real-time pose detection using MediaPipe."""
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1
    ):
        """
        Initialize the pose detector.
        
        Args:
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
            model_complexity: 0, 1, or 2 (higher = more accurate but slower)
        """
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity,
            enable_segmentation=False,
            smooth_landmarks=True
        )
        
    def detect(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Detect pose landmarks in a frame.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            Dictionary containing landmarks and metadata, or None if no pose detected
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        return {
            'landmarks': landmarks,
            'world_landmarks': self._extract_world_landmarks(results)
        }
    
    def _extract_world_landmarks(self, results) -> List[Dict[str, float]]:
        """Extract 3D world coordinates from pose results."""
        if not results.pose_world_landmarks:
            return []
        
        world_landmarks = []
        for landmark in results.pose_world_landmarks.landmark:
            world_landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        return world_landmarks
    
    def draw_landmarks(
        self,
        frame: np.ndarray,
        landmarks: List[Dict[str, float]]
    ) -> np.ndarray:
        """
        Draw pose landmarks on the frame.
        
        Args:
            frame: BGR image from OpenCV
            landmarks: List of landmark dictionaries
            
        Returns:
            Frame with drawn landmarks
        """
        if not landmarks:
            return frame
        
        # Convert landmarks back to MediaPipe format
        mp_landmarks = self.mp_pose.PoseLandmark
        landmark_list = []
        
        for lm in landmarks:
            mp_lm = type('Landmark', (), {})()
            mp_lm.x = lm['x']
            mp_lm.y = lm['y']
            mp_lm.z = lm['z']
            mp_lm.visibility = lm.get('visibility', 1.0)
            landmark_list.append(mp_lm)
        
        # Create a landmark list object
        pose_landmarks = type('PoseLandmarks', (), {})()
        pose_landmarks.landmark = landmark_list
        
        # Draw landmarks
        self.mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        return frame
    
    def close(self):
        """Release resources."""
        self.pose.close()
