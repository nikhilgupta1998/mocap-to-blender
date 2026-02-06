"""
Blender addon for importing motion capture data.

To install:
1. In Blender, go to Edit → Preferences → Add-ons
2. Click "Install" and select this file
3. Enable the "Motion Capture Importer" addon
4. Use File → Import → Motion Capture (.bvh) to import

Or run the generated Python scripts directly in Blender's Text Editor.
"""

bl_info = {
    "name": "Motion Capture Importer",
    "author": "Motion Capture to Blender",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > Motion Capture",
    "description": "Import motion capture data from the mocap-to-blender application",
    "category": "Import-Export",
}

import bpy
import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Quaternion


class ImportMocapData(bpy.types.Operator, ImportHelper):
    """Import Motion Capture Data"""
    bl_idname = "import_scene.mocap_data"
    bl_label = "Import Motion Capture"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
    )

    def execute(self, context):
        return self.import_mocap(context, self.filepath)

    def import_mocap(self, context, filepath):
        """Import motion capture JSON data."""
        # Read JSON file
        with open(filepath, 'r') as f:
            data = json.load(f)

        metadata = data['metadata']
        frames = data['frames']

        # Create armature
        armature = self.create_armature(context)

        # Apply animation
        self.apply_animation(context, armature, frames, metadata)

        self.report({'INFO'}, f"Imported {metadata['frame_count']} frames")
        return {'FINISHED'}

    def create_armature(self, context):
        """Create a basic humanoid armature."""
        # Create armature
        bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
        armature = context.active_object
        armature.name = "MocapArmature"

        # Get armature data
        amt = armature.data
        amt.name = "MocapArmatureData"

        # Clear default bone
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.delete()

        # Bone hierarchy
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

    def apply_animation(self, context, armature, frames, metadata):
        """Apply motion capture animation to armature."""
        # Set scene FPS
        context.scene.render.fps = int(metadata['fps'])

        # Enter pose mode
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        # Apply keyframes
        for frame_idx, frame_data in enumerate(frames):
            frame_number = frame_idx + 1
            context.scene.frame_set(frame_number)

            landmarks = frame_data['landmarks']

            # Set hips position (root bone)
            if len(landmarks) > 24:
                left_hip = landmarks[23]
                right_hip = landmarks[24]

                hips_pos = Vector((
                    (left_hip['x'] + right_hip['x']) / 2,
                    (left_hip['z'] + right_hip['z']) / 2,
                    (left_hip['y'] + right_hip['y']) / 2
                ))

                if 'Hips' in armature.pose.bones:
                    hips_bone = armature.pose.bones['Hips']
                    hips_bone.location = hips_pos
                    hips_bone.keyframe_insert(data_path='location', frame=frame_number)

        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Set timeline
        context.scene.frame_start = 1
        context.scene.frame_end = metadata['frame_count']


def menu_func_import(self, context):
    """Add to import menu."""
    self.layout.operator(ImportMocapData.bl_idname, text="Motion Capture (.json)")


def register():
    """Register addon."""
    bpy.utils.register_class(ImportMocapData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    """Unregister addon."""
    bpy.utils.unregister_class(ImportMocapData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
