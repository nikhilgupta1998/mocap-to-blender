"""
BVH (Biovision Hierarchy) format exporter.
"""
import numpy as np
from typing import List, Dict
from skeleton import BONE_HIERARCHY
from recording import Recording


class BVHExporter:
    """Export motion capture data to BVH format."""
    
    def __init__(self):
        """Initialize the BVH exporter."""
        self.bone_order = self._get_bone_order()
    
    def _get_bone_order(self) -> List[str]:
        """Get bones in hierarchical order for BVH export."""
        return [
            'Hips', 'Spine', 'Chest', 'Neck', 'Head',
            'LeftShoulder', 'LeftUpperArm', 'LeftForeArm', 'LeftHand',
            'RightShoulder', 'RightUpperArm', 'RightForeArm', 'RightHand',
            'LeftUpLeg', 'LeftLeg', 'LeftFoot',
            'RightUpLeg', 'RightLeg', 'RightFoot'
        ]
    
    def export(self, recording: Recording, output_path: str) -> None:
        """
        Export recording to BVH file.
        
        Args:
            recording: Recording data to export
            output_path: Path to save BVH file
        """
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
            offset = child_info.get('offset', [0, 0, 0])
            
            indent_str = '  ' * indent
            lines.append(f'{indent_str}JOINT {child_name}')
            lines.append(f'{indent_str}{{')
            lines.append(f'{indent_str}  OFFSET {offset[0]:.4f} {offset[1]:.4f} {offset[2]:.4f}')
            lines.append(f'{indent_str}  CHANNELS 3 Zrotation Xrotation Yrotation')
            
            # Recursively add children
            self._add_bone_hierarchy(lines, child_name, indent + 1)
            
            # End site for leaf bones
            if not child_info.get('children'):
                lines.append(f'{indent_str}  End Site')
                lines.append(f'{indent_str}  {{')
                lines.append(f'{indent_str}    OFFSET 0.0 0.1 0.0')
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
            # Get bone transformations
            bones = retargeter.retarget_to_blender(frame.landmarks)
            
            # Convert to BVH format (positions and rotations)
            frame_data = []
            
            # Root position (Hips)
            if 'Hips' in bones:
                hips = bones['Hips']
                pos = hips['position']
                frame_data.extend([pos[0], pos[1], pos[2]])
                
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
