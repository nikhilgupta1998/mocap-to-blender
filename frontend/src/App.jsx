import React, { useState } from 'react';
import CameraFeed from './components/CameraFeed';
import Controls from './components/Controls';
import SkeletonPreview from './components/SkeletonPreview';
import ExportPanel from './components/ExportPanel';
import './App.css';

function App() {
  const [landmarks, setLandmarks] = useState([]);
  const [cameraActive, setCameraActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [lastRecording, setLastRecording] = useState(null);

  const handleStatusChange = (status) => {
    if (status.cameraActive !== undefined) {
      setCameraActive(status.cameraActive);
    }
    if (status.recording !== undefined) {
      setRecording(status.recording);
    }
    if (status.lastRecording) {
      setLastRecording(status.lastRecording);
    }
  };

  const handlePoseUpdate = (newLandmarks) => {
    setLandmarks(newLandmarks);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎭 Motion Capture to Blender</h1>
        <p className="subtitle">Real-time pose tracking and animation export</p>
      </header>

      <div className="main-content">
        <div className="left-panel">
          <CameraFeed 
            isActive={cameraActive}
            onPoseUpdate={handlePoseUpdate}
          />
          <SkeletonPreview landmarks={landmarks} />
        </div>

        <div className="right-panel">
          <Controls onStatusChange={handleStatusChange} />
          <ExportPanel lastRecording={lastRecording} />
        </div>
      </div>

      <footer className="app-footer">
        <p>
          Built with MediaPipe, FastAPI, React, and Three.js
        </p>
      </footer>
    </div>
  );
}

export default App;
