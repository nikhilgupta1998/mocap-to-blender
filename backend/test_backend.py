"""
Simple test script to verify backend functionality without a camera.
"""
import sys
import numpy as np
from pose_detector import PoseDetector
from smoother import ExponentialMovingAverage, KalmanFilter
from recording import RecordingManager
from retargeting import BoneRetargeter
from skeleton import Skeleton
from exporters import BVHExporter, BlenderScriptGenerator

def test_pose_detector():
    """Test pose detector initialization."""
    print("Testing PoseDetector...")
    detector = PoseDetector()
    print("✓ PoseDetector initialized")
    detector.close()
    return True

def test_smoothers():
    """Test smoothing filters."""
    print("\nTesting Smoothers...")
    
    # Create dummy landmarks
    landmarks = [
        {'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0}
        for _ in range(33)
    ]
    
    # Test EMA
    ema = ExponentialMovingAverage(alpha=0.3)
    smoothed = ema.smooth(landmarks)
    assert len(smoothed) == 33
    print("✓ EMA filter working")
    
    # Test Kalman
    kalman = KalmanFilter()
    smoothed = kalman.smooth(landmarks)
    assert len(smoothed) == 33
    print("✓ Kalman filter working")
    
    return True

def test_recording():
    """Test recording manager."""
    print("\nTesting RecordingManager...")
    
    manager = RecordingManager()
    
    # Start recording
    session_id = manager.start_recording(fps=30.0)
    print(f"✓ Recording started: {session_id[:8]}...")
    
    # Add some frames
    landmarks = [
        {'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0}
        for _ in range(33)
    ]
    
    for i in range(10):
        manager.add_frame(landmarks)
    print("✓ Added 10 frames")
    
    # Stop recording
    recording = manager.stop_recording()
    assert recording.metadata.frame_count == 10
    print(f"✓ Recording stopped: {recording.metadata.frame_count} frames")
    
    # List recordings
    recordings = manager.list_recordings()
    assert len(recordings) >= 1
    print(f"✓ Found {len(recordings)} recording(s)")
    
    # Cleanup
    manager.delete_recording(session_id)
    print("✓ Recording deleted")
    
    return True

def test_skeleton():
    """Test skeleton representation."""
    print("\nTesting Skeleton...")
    
    skeleton = Skeleton()
    
    landmarks = [
        {'x': 0.5 + i * 0.01, 'y': 0.5 + i * 0.01, 'z': 0.0, 'visibility': 1.0}
        for i in range(33)
    ]
    
    skeleton.update_from_landmarks(landmarks)
    positions = skeleton.get_bone_positions()
    assert len(positions) > 0
    print(f"✓ Skeleton updated with {len(positions)} bones")
    
    return True

def test_retargeting():
    """Test bone retargeting."""
    print("\nTesting BoneRetargeter...")
    
    retargeter = BoneRetargeter()
    
    landmarks = [
        {'x': 0.5 + i * 0.01, 'y': 0.5 + i * 0.01, 'z': 0.0, 'visibility': 1.0}
        for i in range(33)
    ]
    
    bones = retargeter.retarget_to_blender(landmarks)
    assert 'Hips' in bones
    assert 'LeftUpperArm' in bones
    print(f"✓ Retargeted to {len(bones)} bones")
    
    return True

def test_exporters():
    """Test export functionality."""
    print("\nTesting Exporters...")
    
    # Create a test recording
    manager = RecordingManager()
    session_id = manager.start_recording(fps=30.0)
    
    landmarks = [
        {'x': 0.5 + i * 0.001, 'y': 0.5 + i * 0.001, 'z': 0.0, 'visibility': 1.0}
        for i in range(33)
    ]
    
    for _ in range(5):
        manager.add_frame(landmarks)
    
    recording = manager.stop_recording()
    
    # Test BVH export
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(suffix='.bvh', delete=False) as f:
        bvh_path = f.name
    
    try:
        exporter = BVHExporter()
        exporter.export(recording, bvh_path)
        assert os.path.exists(bvh_path)
        print("✓ BVH export successful")
    finally:
        if os.path.exists(bvh_path):
            os.remove(bvh_path)
    
    # Test Blender script export
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        script_path = f.name
    
    try:
        generator = BlenderScriptGenerator()
        generator.generate(recording, script_path)
        assert os.path.exists(script_path)
        print("✓ Blender script export successful")
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
    
    # Cleanup
    manager.delete_recording(session_id)
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Backend Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_pose_detector,
        test_smoothers,
        test_recording,
        test_skeleton,
        test_retargeting,
        test_exporters,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
