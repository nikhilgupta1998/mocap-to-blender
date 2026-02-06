"""
3D skeleton representation and bone hierarchy.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# MediaPipe pose landmark indices
class PoseLandmark:
    """MediaPipe pose landmark indices."""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


# Bone mapping from MediaPipe landmarks to skeleton bones
BONE_MAPPING = {
    'hips': [PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP],
    'spine': [PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP, 
              PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER],
    'chest': [PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER],
    'neck': [PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER, PoseLandmark.NOSE],
    'head': [PoseLandmark.NOSE, PoseLandmark.LEFT_EYE, PoseLandmark.RIGHT_EYE],
    
    'left_shoulder': [PoseLandmark.LEFT_SHOULDER],
    'left_upper_arm': [PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW],
    'left_forearm': [PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST],
    'left_hand': [PoseLandmark.LEFT_WRIST, PoseLandmark.LEFT_INDEX, PoseLandmark.LEFT_PINKY],
    
    'right_shoulder': [PoseLandmark.RIGHT_SHOULDER],
    'right_upper_arm': [PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW],
    'right_forearm': [PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST],
    'right_hand': [PoseLandmark.RIGHT_WRIST, PoseLandmark.RIGHT_INDEX, PoseLandmark.RIGHT_PINKY],
    
    'left_upper_leg': [PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE],
    'left_lower_leg': [PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE],
    'left_foot': [PoseLandmark.LEFT_ANKLE, PoseLandmark.LEFT_HEEL, PoseLandmark.LEFT_FOOT_INDEX],
    
    'right_upper_leg': [PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE],
    'right_lower_leg': [PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE],
    'right_foot': [PoseLandmark.RIGHT_ANKLE, PoseLandmark.RIGHT_HEEL, PoseLandmark.RIGHT_FOOT_INDEX],
}


# Bone hierarchy for BVH export
BONE_HIERARCHY = {
    'Hips': {
        'children': ['Spine', 'LeftUpLeg', 'RightUpLeg'],
        'offset': [0, 0, 0]
    },
    'Spine': {
        'parent': 'Hips',
        'children': ['Chest'],
        'offset': [0, 0.1, 0]
    },
    'Chest': {
        'parent': 'Spine',
        'children': ['Neck', 'LeftShoulder', 'RightShoulder'],
        'offset': [0, 0.15, 0]
    },
    'Neck': {
        'parent': 'Chest',
        'children': ['Head'],
        'offset': [0, 0.1, 0]
    },
    'Head': {
        'parent': 'Neck',
        'children': [],
        'offset': [0, 0.1, 0]
    },
    'LeftShoulder': {
        'parent': 'Chest',
        'children': ['LeftUpperArm'],
        'offset': [-0.05, 0.05, 0]
    },
    'LeftUpperArm': {
        'parent': 'LeftShoulder',
        'children': ['LeftForeArm'],
        'offset': [-0.25, 0, 0]
    },
    'LeftForeArm': {
        'parent': 'LeftUpperArm',
        'children': ['LeftHand'],
        'offset': [-0.25, 0, 0]
    },
    'LeftHand': {
        'parent': 'LeftForeArm',
        'children': [],
        'offset': [-0.1, 0, 0]
    },
    'RightShoulder': {
        'parent': 'Chest',
        'children': ['RightUpperArm'],
        'offset': [0.05, 0.05, 0]
    },
    'RightUpperArm': {
        'parent': 'RightShoulder',
        'children': ['RightForeArm'],
        'offset': [0.25, 0, 0]
    },
    'RightForeArm': {
        'parent': 'RightUpperArm',
        'children': ['RightHand'],
        'offset': [0.25, 0, 0]
    },
    'RightHand': {
        'parent': 'RightForeArm',
        'children': [],
        'offset': [0.1, 0, 0]
    },
    'LeftUpLeg': {
        'parent': 'Hips',
        'children': ['LeftLeg'],
        'offset': [-0.1, -0.05, 0]
    },
    'LeftLeg': {
        'parent': 'LeftUpLeg',
        'children': ['LeftFoot'],
        'offset': [0, -0.4, 0]
    },
    'LeftFoot': {
        'parent': 'LeftLeg',
        'children': [],
        'offset': [0, -0.4, 0]
    },
    'RightUpLeg': {
        'parent': 'Hips',
        'children': ['RightLeg'],
        'offset': [0.1, -0.05, 0]
    },
    'RightLeg': {
        'parent': 'RightUpLeg',
        'children': ['RightFoot'],
        'offset': [0, -0.4, 0]
    },
    'RightFoot': {
        'parent': 'RightLeg',
        'children': [],
        'offset': [0, -0.4, 0]
    },
}


@dataclass
class Bone:
    """Represents a bone in the skeleton."""
    name: str
    parent: Optional[str]
    children: List[str]
    position: np.ndarray
    rotation: np.ndarray  # Quaternion [w, x, y, z]
    length: float


class Skeleton:
    """3D skeleton representation."""
    
    def __init__(self):
        """Initialize the skeleton."""
        self.bones: Dict[str, Bone] = {}
        self.root_position = np.array([0.0, 0.0, 0.0])
    
    def update_from_landmarks(
        self,
        landmarks: List[Dict[str, float]]
    ) -> None:
        """
        Update skeleton from MediaPipe landmarks.
        
        Args:
            landmarks: List of landmark dictionaries with x, y, z coordinates
        """
        # Calculate bone positions
        for bone_name, landmark_indices in BONE_MAPPING.items():
            position = self._calculate_bone_position(landmarks, landmark_indices)
            
            # Calculate bone rotation (simplified - would need proper rotation calculation)
            rotation = np.array([1.0, 0.0, 0.0, 0.0])  # Identity quaternion
            
            # Calculate bone length
            if len(landmark_indices) >= 2:
                start_pos = np.array([
                    landmarks[landmark_indices[0]]['x'],
                    landmarks[landmark_indices[0]]['y'],
                    landmarks[landmark_indices[0]]['z']
                ])
                end_pos = np.array([
                    landmarks[landmark_indices[-1]]['x'],
                    landmarks[landmark_indices[-1]]['y'],
                    landmarks[landmark_indices[-1]]['z']
                ])
                length = np.linalg.norm(end_pos - start_pos)
            else:
                length = 0.0
            
            # Create or update bone
            parent = BONE_HIERARCHY.get(bone_name.replace('_', '').title(), {}).get('parent')
            children = BONE_HIERARCHY.get(bone_name.replace('_', '').title(), {}).get('children', [])
            
            self.bones[bone_name] = Bone(
                name=bone_name,
                parent=parent,
                children=children,
                position=position,
                rotation=rotation,
                length=length
            )
        
        # Update root position (average of hips)
        if landmarks and len(landmarks) > max(PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP):
            left_hip = landmarks[PoseLandmark.LEFT_HIP]
            right_hip = landmarks[PoseLandmark.RIGHT_HIP]
            self.root_position = np.array([
                (left_hip['x'] + right_hip['x']) / 2,
                (left_hip['y'] + right_hip['y']) / 2,
                (left_hip['z'] + right_hip['z']) / 2
            ])
    
    def _calculate_bone_position(
        self,
        landmarks: List[Dict[str, float]],
        indices: List[int]
    ) -> np.ndarray:
        """Calculate bone position as average of landmark positions."""
        positions = []
        for idx in indices:
            if idx < len(landmarks):
                lm = landmarks[idx]
                positions.append([lm['x'], lm['y'], lm['z']])
        
        if not positions:
            return np.array([0.0, 0.0, 0.0])
        
        return np.mean(positions, axis=0)
    
    def get_bone_positions(self) -> Dict[str, np.ndarray]:
        """Get positions of all bones."""
        return {name: bone.position for name, bone in self.bones.items()}
    
    def get_bone_rotations(self) -> Dict[str, np.ndarray]:
        """Get rotations of all bones."""
        return {name: bone.rotation for name, bone in self.bones.items()}
