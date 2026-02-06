"""
Retargeting module for mapping MediaPipe joints to Blender armature bones.
"""
import numpy as np
from typing import List, Dict, Tuple
from scipy.spatial.transform import Rotation


def vector_to_rotation(vec_from: np.ndarray, vec_to: np.ndarray) -> np.ndarray:
    """
    Calculate rotation quaternion from one vector to another.
    
    Args:
        vec_from: Source vector
        vec_to: Target vector
        
    Returns:
        Quaternion [w, x, y, z]
    """
    vec_from = vec_from / (np.linalg.norm(vec_from) + 1e-8)
    vec_to = vec_to / (np.linalg.norm(vec_to) + 1e-8)
    
    # Calculate rotation axis and angle
    axis = np.cross(vec_from, vec_to)
    axis_length = np.linalg.norm(axis)
    
    if axis_length < 1e-6:
        # Vectors are parallel
        if np.dot(vec_from, vec_to) > 0:
            return np.array([1.0, 0.0, 0.0, 0.0])  # Identity
        else:
            # 180-degree rotation
            perpendicular = np.array([1.0, 0.0, 0.0])
            if abs(vec_from[0]) > 0.9:
                perpendicular = np.array([0.0, 1.0, 0.0])
            axis = np.cross(vec_from, perpendicular)
            axis = axis / np.linalg.norm(axis)
            return np.array([0.0, axis[0], axis[1], axis[2]])
    
    axis = axis / axis_length
    angle = np.arccos(np.clip(np.dot(vec_from, vec_to), -1.0, 1.0))
    
    # Convert to quaternion
    half_angle = angle / 2
    w = np.cos(half_angle)
    xyz = axis * np.sin(half_angle)
    
    return np.array([w, xyz[0], xyz[1], xyz[2]])


def calculate_bone_rotation(
    start_pos: np.ndarray,
    end_pos: np.ndarray,
    reference_direction: np.ndarray = np.array([0, 1, 0])
) -> np.ndarray:
    """
    Calculate bone rotation from start and end positions.
    
    Args:
        start_pos: Starting position of the bone
        end_pos: Ending position of the bone
        reference_direction: Reference direction for the bone
        
    Returns:
        Rotation quaternion [w, x, y, z]
    """
    bone_direction = end_pos - start_pos
    return vector_to_rotation(reference_direction, bone_direction)


class BoneRetargeter:
    """Retargets MediaPipe landmarks to Blender bone rotations."""
    
    def __init__(self):
        """Initialize the retargeter."""
        self.t_pose_offsets = self._initialize_t_pose()
    
    def _initialize_t_pose(self) -> Dict[str, np.ndarray]:
        """Initialize T-pose reference rotations."""
        return {
            'Hips': np.array([1.0, 0.0, 0.0, 0.0]),
            'Spine': np.array([1.0, 0.0, 0.0, 0.0]),
            'Chest': np.array([1.0, 0.0, 0.0, 0.0]),
            'Neck': np.array([1.0, 0.0, 0.0, 0.0]),
            'Head': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftShoulder': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftUpperArm': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftForeArm': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftHand': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightShoulder': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightUpperArm': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightForeArm': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightHand': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftUpLeg': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftLeg': np.array([1.0, 0.0, 0.0, 0.0]),
            'LeftFoot': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightUpLeg': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightLeg': np.array([1.0, 0.0, 0.0, 0.0]),
            'RightFoot': np.array([1.0, 0.0, 0.0, 0.0]),
        }
    
    def retarget_to_blender(
        self,
        landmarks: List[Dict[str, float]]
    ) -> Dict[str, Dict[str, any]]:
        """
        Retarget MediaPipe landmarks to Blender bone transformations.
        
        Args:
            landmarks: List of MediaPipe landmark dictionaries
            
        Returns:
            Dictionary of bone names to transformations (position, rotation)
        """
        if not landmarks or len(landmarks) < 33:
            return {}
        
        bones = {}
        
        # Convert landmarks to numpy arrays for easier calculation
        lm_array = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        
        # Calculate hips (root)
        hips_pos = (lm_array[23] + lm_array[24]) / 2
        bones['Hips'] = {
            'position': hips_pos.tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        # Calculate spine bones
        spine_pos = (lm_array[11] + lm_array[12] + lm_array[23] + lm_array[24]) / 4
        chest_pos = (lm_array[11] + lm_array[12]) / 2
        
        bones['Spine'] = {
            'position': spine_pos.tolist(),
            'rotation': calculate_bone_rotation(hips_pos, chest_pos).tolist()
        }
        
        bones['Chest'] = {
            'position': chest_pos.tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        # Neck and head
        neck_pos = chest_pos
        head_pos = lm_array[0]
        
        bones['Neck'] = {
            'position': neck_pos.tolist(),
            'rotation': calculate_bone_rotation(neck_pos, head_pos).tolist()
        }
        
        bones['Head'] = {
            'position': head_pos.tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        # Left arm
        bones['LeftShoulder'] = {
            'position': lm_array[11].tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        bones['LeftUpperArm'] = {
            'position': lm_array[11].tolist(),
            'rotation': calculate_bone_rotation(lm_array[11], lm_array[13]).tolist()
        }
        
        bones['LeftForeArm'] = {
            'position': lm_array[13].tolist(),
            'rotation': calculate_bone_rotation(lm_array[13], lm_array[15]).tolist()
        }
        
        bones['LeftHand'] = {
            'position': lm_array[15].tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        # Right arm
        bones['RightShoulder'] = {
            'position': lm_array[12].tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        bones['RightUpperArm'] = {
            'position': lm_array[12].tolist(),
            'rotation': calculate_bone_rotation(lm_array[12], lm_array[14]).tolist()
        }
        
        bones['RightForeArm'] = {
            'position': lm_array[14].tolist(),
            'rotation': calculate_bone_rotation(lm_array[14], lm_array[16]).tolist()
        }
        
        bones['RightHand'] = {
            'position': lm_array[16].tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        # Left leg
        bones['LeftUpLeg'] = {
            'position': lm_array[23].tolist(),
            'rotation': calculate_bone_rotation(lm_array[23], lm_array[25]).tolist()
        }
        
        bones['LeftLeg'] = {
            'position': lm_array[25].tolist(),
            'rotation': calculate_bone_rotation(lm_array[25], lm_array[27]).tolist()
        }
        
        bones['LeftFoot'] = {
            'position': lm_array[27].tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        # Right leg
        bones['RightUpLeg'] = {
            'position': lm_array[24].tolist(),
            'rotation': calculate_bone_rotation(lm_array[24], lm_array[26]).tolist()
        }
        
        bones['RightLeg'] = {
            'position': lm_array[26].tolist(),
            'rotation': calculate_bone_rotation(lm_array[26], lm_array[28]).tolist()
        }
        
        bones['RightFoot'] = {
            'position': lm_array[28].tolist(),
            'rotation': [1.0, 0.0, 0.0, 0.0]
        }
        
        return bones
    
    def euler_to_quaternion(self, euler: Tuple[float, float, float]) -> np.ndarray:
        """Convert Euler angles to quaternion."""
        rotation = Rotation.from_euler('xyz', euler, degrees=False)
        quat = rotation.as_quat()
        # Convert from [x, y, z, w] to [w, x, y, z]
        return np.array([quat[3], quat[0], quat[1], quat[2]])
    
    def quaternion_to_euler(self, quat: np.ndarray) -> Tuple[float, float, float]:
        """Convert quaternion to Euler angles."""
        # Convert from [w, x, y, z] to [x, y, z, w]
        rotation = Rotation.from_quat([quat[1], quat[2], quat[3], quat[0]])
        return tuple(rotation.as_euler('xyz', degrees=False))
