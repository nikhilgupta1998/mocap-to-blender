"""
BVH (Biovision Hierarchy) format exporter.
"""
import numpy as np
from typing import List, Dict, Optional
from skeleton import BONE_HIERARCHY, PoseLandmark
from recording import Recording


# Scale factor to convert MediaPipe meters to Blender units
# MediaPipe world landmarks are in meters, multiply by 100 for cm-scale in Blender
SCALE_FACTOR = 100.0


class BVHExporter:
    """Export motion capture data to BVH format."""
    
    def __init__(self):
        """Initialize the BVH exporter."""
        self.bone_order = self._get_bone_order()
        self.bone_offsets = {}  # Will be calculated from recording data
    
    def _get_bone_order(self) -> List[str]:
        """Get bones in hierarchical order for BVH export."""
        return [
            'Hips', 'Spine', 'Chest', 'Neck', 'Head',
            'LeftShoulder', 'LeftUpperArm', 'LeftForeArm', 'LeftHand',
            'RightShoulder', 'RightUpperArm', 'RightForeArm', 'RightHand',
            'LeftUpLeg', 'LeftLeg', 'LeftFoot',
            'RightUpLeg', 'RightLeg', 'RightFoot'
        ]
    
    def _calculate_bone_offsets(self, recording: Recording) -> None:
        """
        Calculate bone offsets from actual pose data.
        Uses the first frame or average of first few frames for stable measurements.
        
        Args:
            recording: Recording data containing world landmarks
        """
        if not recording.frames:
            # Use default small offsets if no frames
            self.bone_offsets = {bone: info.get('offset', [0, 0, 0]) 
                               for bone, info in BONE_HIERARCHY.items()}
            return
        
        # Use first frame to calculate offsets
        first_frame = recording.frames[0]
        world_landmarks = first_frame.world_landmarks
        
        # Fallback to screen landmarks if world landmarks not available
        if not world_landmarks:
            world_landmarks = first_frame.landmarks
        
        # Convert to numpy array for easier calculation
        # Note: List comprehension used for compatibility with dict-like landmark objects
        lm_array = np.array([[lm['x'], lm['y'], lm['z']] for lm in world_landmarks])
        
        # Calculate bone offsets based on MediaPipe landmark positions
        self.bone_offsets = {}
        
        # Hips (root) - no offset
        self.bone_offsets['Hips'] = [0.0, 0.0, 0.0]
        
        # Spine - from hips to mid-torso
        hips_pos = (lm_array[PoseLandmark.LEFT_HIP] + lm_array[PoseLandmark.RIGHT_HIP]) / 2
        shoulders_pos = (lm_array[PoseLandmark.LEFT_SHOULDER] + lm_array[PoseLandmark.RIGHT_SHOULDER]) / 2
        spine_offset = (shoulders_pos - hips_pos) * 0.5  # Halfway up the torso
        self.bone_offsets['Spine'] = (spine_offset * SCALE_FACTOR).tolist()
        
        # Chest - from spine to shoulders
        chest_offset = spine_offset  # Same length as spine
        self.bone_offsets['Chest'] = (chest_offset * SCALE_FACTOR).tolist()
        
        # Neck - from shoulders to nose (approximate)
        neck_offset = (lm_array[PoseLandmark.NOSE] - shoulders_pos) * 0.5
        self.bone_offsets['Neck'] = (neck_offset * SCALE_FACTOR).tolist()
        
        # Head - from neck to top
        head_offset = (lm_array[PoseLandmark.NOSE] - shoulders_pos) * 0.5
        self.bone_offsets['Head'] = (head_offset * SCALE_FACTOR).tolist()
        
        # Left arm chain
        left_shoulder_offset = lm_array[PoseLandmark.LEFT_SHOULDER] - shoulders_pos
        self.bone_offsets['LeftShoulder'] = (left_shoulder_offset * SCALE_FACTOR).tolist()
        
        left_upper_arm_offset = lm_array[PoseLandmark.LEFT_ELBOW] - lm_array[PoseLandmark.LEFT_SHOULDER]
        self.bone_offsets['LeftUpperArm'] = (left_upper_arm_offset * SCALE_FACTOR).tolist()
        
        left_forearm_offset = lm_array[PoseLandmark.LEFT_WRIST] - lm_array[PoseLandmark.LEFT_ELBOW]
        self.bone_offsets['LeftForeArm'] = (left_forearm_offset * SCALE_FACTOR).tolist()
        
        left_hand_offset = (lm_array[PoseLandmark.LEFT_INDEX] - lm_array[PoseLandmark.LEFT_WRIST]) * 0.5
        self.bone_offsets['LeftHand'] = (left_hand_offset * SCALE_FACTOR).tolist()
        
        # Right arm chain
        right_shoulder_offset = lm_array[PoseLandmark.RIGHT_SHOULDER] - shoulders_pos
        self.bone_offsets['RightShoulder'] = (right_shoulder_offset * SCALE_FACTOR).tolist()
        
        right_upper_arm_offset = lm_array[PoseLandmark.RIGHT_ELBOW] - lm_array[PoseLandmark.RIGHT_SHOULDER]
        self.bone_offsets['RightUpperArm'] = (right_upper_arm_offset * SCALE_FACTOR).tolist()
        
        right_forearm_offset = lm_array[PoseLandmark.RIGHT_WRIST] - lm_array[PoseLandmark.RIGHT_ELBOW]
        self.bone_offsets['RightForeArm'] = (right_forearm_offset * SCALE_FACTOR).tolist()
        
        right_hand_offset = (lm_array[PoseLandmark.RIGHT_INDEX] - lm_array[PoseLandmark.RIGHT_WRIST]) * 0.5
        self.bone_offsets['RightHand'] = (right_hand_offset * SCALE_FACTOR).tolist()
        
        # Left leg chain
        left_upleg_offset = lm_array[PoseLandmark.LEFT_HIP] - hips_pos
        self.bone_offsets['LeftUpLeg'] = (left_upleg_offset * SCALE_FACTOR).tolist()
        
        left_leg_offset = lm_array[PoseLandmark.LEFT_KNEE] - lm_array[PoseLandmark.LEFT_HIP]
        self.bone_offsets['LeftLeg'] = (left_leg_offset * SCALE_FACTOR).tolist()
        
        left_foot_offset = lm_array[PoseLandmark.LEFT_ANKLE] - lm_array[PoseLandmark.LEFT_KNEE]
        self.bone_offsets['LeftFoot'] = (left_foot_offset * SCALE_FACTOR).tolist()
        
        # Right leg chain
        right_upleg_offset = lm_array[PoseLandmark.RIGHT_HIP] - hips_pos
        self.bone_offsets['RightUpLeg'] = (right_upleg_offset * SCALE_FACTOR).tolist()
        
        right_leg_offset = lm_array[PoseLandmark.RIGHT_KNEE] - lm_array[PoseLandmark.RIGHT_HIP]
        self.bone_offsets['RightLeg'] = (right_leg_offset * SCALE_FACTOR).tolist()
        
        right_foot_offset = lm_array[PoseLandmark.RIGHT_ANKLE] - lm_array[PoseLandmark.RIGHT_KNEE]
        self.bone_offsets['RightFoot'] = (right_foot_offset * SCALE_FACTOR).tolist()
    
    def export(self, recording: Recording, output_path: str) -> None:
        """
        Export recording to BVH file.
        
        Args:
            recording: Recording data to export
            output_path: Path to save BVH file
        """
        # Calculate bone offsets from the recording data
        self._calculate_bone_offsets(recording)
        
        bvh_content = self._generate_bvh(recording)
        
        with open(output_path, 'w') as f:
            f.write(bvh_content)
    
    def _generate_bvh(self, recording: Recording) -> str:
        """Generate BVH file content."""
        # Generate hierarchy section
        hierarchy = self._generate_hierarchy()
        
        # Generate motion section
        motion = self._generate_motion(recording)
        
        return hierarchy + '\n' + motion
    
    def _generate_hierarchy(self) -> str:
        """Generate BVH hierarchy section."""
        lines = ['HIERARCHY']
        
        # Start with root bone (Hips)
        lines.append('ROOT Hips')
        lines.append('{')
        lines.append('  OFFSET 0.0 0.0 0.0')
        lines.append('  CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation')
        
        # Add child bones recursively
        self._add_bone_hierarchy(lines, 'Hips', indent=1)
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def _add_bone_hierarchy(
        self,
        lines: List[str],
        bone_name: str,
        indent: int
    ) -> None:
        """Recursively add bone hierarchy."""
        bone_info = BONE_HIERARCHY.get(bone_name, {})
        children = bone_info.get('children', [])
        
        for child_name in children:
            child_info = BONE_HIERARCHY.get(child_name, {})
            
            # Use calculated offsets if available, otherwise use defaults
            offset = self.bone_offsets.get(child_name, child_info.get('offset', [0, 0, 0]))
            
            indent_str = '  ' * indent
            lines.append(f'{indent_str}JOINT {child_name}')
            lines.append(f'{indent_str}{{')
            lines.append(f'{indent_str}  OFFSET {offset[0]:.4f} {offset[1]:.4f} {offset[2]:.4f}')
            lines.append(f'{indent_str}  CHANNELS 3 Zrotation Xrotation Yrotation')
            
            # Recursively add children
            self._add_bone_hierarchy(lines, child_name, indent + 1)
            
            # End site for leaf bones
            if not child_info.get('children'):
                # Calculate end site offset as a small extension of the bone
                # Use 10% of bone offset magnitude as end site length
                bone_length = np.linalg.norm(offset)
                if bone_length > 1.0:
                    # For bones with significant length, extend 10% in same direction
                    end_offset = [offset[0] * 0.1, offset[1] * 0.1, offset[2] * 0.1]
                else:
                    # For very small bones, use a minimum end site offset
                    MIN_END_SITE_OFFSET = 5.0  # Minimum offset in Blender units
                    end_offset = [0.0, MIN_END_SITE_OFFSET, 0.0]
                
                lines.append(f'{indent_str}  End Site')
                lines.append(f'{indent_str}  {{')
                lines.append(f'{indent_str}    OFFSET {end_offset[0]:.4f} {end_offset[1]:.4f} {end_offset[2]:.4f}')
                lines.append(f'{indent_str}  }}')
            
            lines.append(f'{indent_str}}}')
    
    def _generate_motion(self, recording: Recording) -> str:
        """Generate BVH motion section."""
        lines = ['MOTION']
        lines.append(f'Frames: {recording.metadata.frame_count}')
        
        frame_time = 1.0 / recording.metadata.fps
        lines.append(f'Frame Time: {frame_time:.6f}')
        
        # Generate frame data
        from retargeting import BoneRetargeter
        retargeter = BoneRetargeter()
        
        for frame in recording.frames:
            # Use world_landmarks if available, otherwise fallback to screen landmarks
            landmarks = frame.world_landmarks if frame.world_landmarks else frame.landmarks
            
            # Get bone transformations
            bones = retargeter.retarget_to_blender(landmarks)
            
            # Convert to BVH format (positions and rotations)
            frame_data = []
            
            # Root position (Hips) - use world coordinates and scale
            if 'Hips' in bones:
                hips = bones['Hips']
                pos = hips['position']
                # Apply scale factor to convert from meters to Blender units
                frame_data.extend([
                    pos[0] * SCALE_FACTOR,
                    pos[1] * SCALE_FACTOR,
                    pos[2] * SCALE_FACTOR
                ])
                
                # Root rotation (convert quaternion to Euler)
                rot_quat = hips['rotation']
                rot_euler = retargeter.quaternion_to_euler(np.array(rot_quat))
                frame_data.extend([
                    np.degrees(rot_euler[2]),  # Z
                    np.degrees(rot_euler[0]),  # X
                    np.degrees(rot_euler[1])   # Y
                ])
            else:
                frame_data.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            
            # Other bones (rotations only)
            for bone_name in self.bone_order[1:]:  # Skip Hips (already added)
                if bone_name in bones:
                    rot_quat = bones[bone_name]['rotation']
                    rot_euler = retargeter.quaternion_to_euler(np.array(rot_quat))
                    frame_data.extend([
                        np.degrees(rot_euler[2]),  # Z
                        np.degrees(rot_euler[0]),  # X
                        np.degrees(rot_euler[1])   # Y
                    ])
                else:
                    frame_data.extend([0.0, 0.0, 0.0])
            
            # Format frame data
            frame_str = ' '.join([f'{val:.6f}' for val in frame_data])
            lines.append(frame_str)
        
        return '\n'.join(lines)
