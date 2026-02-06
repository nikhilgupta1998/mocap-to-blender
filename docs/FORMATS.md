# Export Formats

## BVH (Biovision Hierarchy)

BVH is the industry standard format for motion capture data. It's widely supported by 3D animation software including Blender, Maya, MotionBuilder, and Unity.

### File Structure

```
HIERARCHY
ROOT Hips
{
  OFFSET 0.0 0.0 0.0
  CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
  JOINT Spine
  {
    OFFSET 0.0 0.1 0.0
    CHANNELS 3 Zrotation Xrotation Yrotation
    JOINT Chest
    {
      ...
    }
  }
}
MOTION
Frames: 300
Frame Time: 0.033333
<frame data>
```

### Bone Hierarchy

The exported BVH uses this bone hierarchy:

```
Hips (Root)
├── Spine
│   └── Chest
│       ├── Neck
│       │   └── Head
│       ├── LeftShoulder
│       │   └── LeftUpperArm
│       │       └── LeftForeArm
│       │           └── LeftHand
│       └── RightShoulder
│           └── RightUpperArm
│               └── RightForeArm
│                   └── RightHand
├── LeftUpLeg
│   └── LeftLeg
│       └── LeftFoot
└── RightUpLeg
    └── RightLeg
        └── RightFoot
```

### Importing into Blender

1. In Blender, go to **File → Import → Motion Capture (.bvh)**
2. Select your exported `.bvh` file
3. Adjust import settings:
   - Scale: 1.0 (adjust if needed)
   - Rotate: None
   - Start Frame: 1
4. Click **Import BVH**

The animation will be imported with a basic skeleton. You can then retarget it to your character rig.

### Compatibility

- ✅ Blender 2.8+
- ✅ Maya
- ✅ MotionBuilder
- ✅ Unity
- ✅ Unreal Engine
- ✅ Mixamo (with some adjustments)

## Blender Python Script

A ready-to-use Python script that creates a skeleton and applies the animation directly in Blender.

### Features

- Creates a complete humanoid armature
- Applies motion capture data as keyframes
- Sets up proper bone hierarchy
- Configures timeline and playback settings

### Usage

1. Open Blender
2. Go to **Scripting** workspace
3. Click **Open** and select your exported `.py` file
4. Click **Run Script** (or press Alt+P)
5. The skeleton will be created and animated

### Script Output

The script will:
- Create an armature named "MocapArmature"
- Add 19 bones in proper hierarchy
- Apply animation keyframes
- Set timeline to match recording duration
- Print import summary to console

### Customization

You can edit the generated script to:
- Adjust bone lengths (edit `offset` values)
- Change armature name
- Modify bone hierarchy
- Add custom bone properties

## MediaPipe Landmarks

Both export formats use MediaPipe's 33 pose landmarks:

### Landmark Indices

```
0:  Nose
1-10: Face landmarks
11-12: Shoulders (Left, Right)
13-14: Elbows (Left, Right)
15-16: Wrists (Left, Right)
17-22: Hand landmarks
23-24: Hips (Left, Right)
25-26: Knees (Left, Right)
27-28: Ankles (Left, Right)
29-32: Foot landmarks
```

### Coordinate System

- **X**: Horizontal (left-right)
- **Y**: Vertical (up-down)
- **Z**: Depth (forward-backward)

Values are normalized:
- X, Y: 0.0 to 1.0 (image coordinates)
- Z: Real-world depth estimation (meters, relative to hips)

## Bone Mapping

MediaPipe landmarks → Blender bones:

| Blender Bone | MediaPipe Landmarks |
|--------------|---------------------|
| Hips | Average of 23, 24 |
| Spine | 23, 24, 11, 12 |
| Chest | 11, 12 |
| Neck | 11, 12, 0 |
| Head | 0, 1, 2, 3, 4 |
| LeftShoulder | 11 |
| LeftUpperArm | 11 → 13 |
| LeftForeArm | 13 → 15 |
| LeftHand | 15, 17, 19, 21 |
| RightShoulder | 12 |
| RightUpperArm | 12 → 14 |
| RightForeArm | 14 → 16 |
| RightHand | 16, 18, 20, 22 |
| LeftUpLeg | 23 → 25 |
| LeftLeg | 25 → 27 |
| LeftFoot | 27, 29, 31 |
| RightUpLeg | 24 → 26 |
| RightLeg | 26 → 28 |
| RightFoot | 28, 30, 32 |

## Future Formats

Planned support for:
- **FBX**: Universal 3D format with materials and meshes
- **glTF**: Web-friendly 3D format
- **Alembic**: For complex animation caching
- **USD**: Universal Scene Description

## Tips

### For Best Results

1. **Lighting**: Ensure good, even lighting for accurate pose detection
2. **Background**: Plain background improves detection accuracy
3. **Distance**: Stand 1.5-2 meters from camera for optimal tracking
4. **Full Body**: Ensure full body is visible in frame
5. **Duration**: Keep recordings under 30 seconds for manageable file sizes

### Retargeting to Custom Rigs

The exported skeleton uses standard bone names compatible with:
- Rigify (Blender addon)
- Mixamo Auto-Rigger
- Unity Humanoid
- Unreal Engine Mannequin

For custom rigs, you may need to:
1. Import BVH animation
2. Use constraint-based retargeting
3. Bake animation to your custom rig
4. Delete the imported skeleton
