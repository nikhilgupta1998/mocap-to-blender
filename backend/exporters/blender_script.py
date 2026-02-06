"""
Blender Python script generator for importing motion capture data.
"""
from typing import List, Dict
from recording import Recording


class BlenderScriptGenerator:
    """Generate Blender Python scripts for importing mocap data."""
    
    def generate(self, recording: Recording, output_path: str) -> None:
        """
        Generate Blender import script.
        
        Args:
            recording: Recording data
            output_path: Path to save Python script
        """
        script_content = self._generate_script(recording)
        
        with open(output_path, 'w') as f:
            f.write(script_content)
    
    def _generate_script(self, recording: Recording) -> str:
        """Generate the Blender script content."""
        script = '''"""
Motion Capture Import Script for Blender
Generated automatically - import this script in Blender's Text Editor and run it.
"""
import bpy
import math
from mathutils import Vector, Quaternion

# Recording metadata
RECORDING_INFO = {
    'session_id': '%s',
    'fps': %f,
    'frame_count': %d,
    'duration': %f
}

# Frame data (landmarks for each frame)
FRAME_DATA = %s

def create_armature():
    """Create a basic humanoid armature."""
    # Create armature
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = "MocapArmature"
    
    # Get armature data
    amt = armature.data
    amt.name = "MocapArmatureData"
    
    # Clear default bone
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()
    
    # Bone hierarchy definition
    bones_to_create = [
        ('Hips', None, (0, 0, 0), (0, 0.1, 0)),
        ('Spine', 'Hips', (0, 0.1, 0), (0, 0.25, 0)),
        ('Chest', 'Spine', (0, 0.25, 0), (0, 0.4, 0)),
        ('Neck', 'Chest', (0, 0.4, 0), (0, 0.5, 0)),
        ('Head', 'Neck', (0, 0.5, 0), (0, 0.6, 0)),
        
        ('LeftShoulder', 'Chest', (-0.05, 0.4, 0), (-0.1, 0.4, 0)),
        ('LeftUpperArm', 'LeftShoulder', (-0.1, 0.4, 0), (-0.35, 0.4, 0)),
        ('LeftForeArm', 'LeftUpperArm', (-0.35, 0.4, 0), (-0.6, 0.4, 0)),
        ('LeftHand', 'LeftForeArm', (-0.6, 0.4, 0), (-0.7, 0.4, 0)),
        
        ('RightShoulder', 'Chest', (0.05, 0.4, 0), (0.1, 0.4, 0)),
        ('RightUpperArm', 'RightShoulder', (0.1, 0.4, 0), (0.35, 0.4, 0)),
        ('RightForeArm', 'RightUpperArm', (0.35, 0.4, 0), (0.6, 0.4, 0)),
        ('RightHand', 'RightForeArm', (0.6, 0.4, 0), (0.7, 0.4, 0)),
        
        ('LeftUpLeg', 'Hips', (-0.1, 0, 0), (-0.1, -0.4, 0)),
        ('LeftLeg', 'LeftUpLeg', (-0.1, -0.4, 0), (-0.1, -0.8, 0)),
        ('LeftFoot', 'LeftLeg', (-0.1, -0.8, 0), (-0.1, -0.9, 0.1)),
        
        ('RightUpLeg', 'Hips', (0.1, 0, 0), (0.1, -0.4, 0)),
        ('RightLeg', 'RightUpLeg', (0.1, -0.4, 0), (0.1, -0.8, 0)),
        ('RightFoot', 'RightLeg', (0.1, -0.8, 0), (0.1, -0.9, 0.1)),
    ]
    
    # Create bones
    created_bones = {}
    for bone_name, parent_name, head, tail in bones_to_create:
        bone = amt.edit_bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        
        if parent_name and parent_name in created_bones:
            bone.parent = created_bones[parent_name]
        
        created_bones[bone_name] = bone
    
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return armature

def apply_animation(armature):
    """Apply motion capture animation to armature."""
    # Set scene FPS
    bpy.context.scene.render.fps = int(RECORDING_INFO['fps'])
    
    # Enter pose mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Apply keyframes for each frame
    for frame_idx, frame_data in enumerate(FRAME_DATA):
        frame_number = frame_idx + 1
        bpy.context.scene.frame_set(frame_number)
        
        landmarks = frame_data['landmarks']
        
        # Simple position-based animation for hips
        if len(landmarks) > 24:
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            # Calculate hips position
            hips_pos = Vector((
                (left_hip['x'] + right_hip['x']) / 2,
                (left_hip['z'] + right_hip['z']) / 2,
                (left_hip['y'] + right_hip['y']) / 2
            ))
            
            # Set hips location
            if 'Hips' in armature.pose.bones:
                hips_bone = armature.pose.bones['Hips']
                hips_bone.location = hips_pos
                hips_bone.keyframe_insert(data_path='location', frame=frame_number)
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def main():
    """Main execution function."""
    print(f"Importing motion capture data...")
    print(f"Session ID: {RECORDING_INFO['session_id']}")
    print(f"Frames: {RECORDING_INFO['frame_count']}")
    print(f"FPS: {RECORDING_INFO['fps']}")
    print(f"Duration: {RECORDING_INFO['duration']:.2f}s")
    
    # Create armature
    armature = create_armature()
    print("Armature created")
    
    # Apply animation
    apply_animation(armature)
    print("Animation applied")
    
    # Set timeline
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = RECORDING_INFO['frame_count']
    
    print("Import complete!")

if __name__ == "__main__":
    main()
''' % (
            recording.metadata.session_id,
            recording.metadata.fps,
            recording.metadata.frame_count,
            recording.metadata.duration,
            str([{
                'frame_id': frame.frame_id,
                'timestamp': frame.timestamp,
                'landmarks': frame.landmarks
            } for frame in recording.frames])
        )
        
        return script
