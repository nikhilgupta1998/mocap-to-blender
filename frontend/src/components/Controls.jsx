import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { websocketService } from '../services/websocket';

const Controls = ({ onStatusChange }) => {
  const [cameraActive, setCameraActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [frameCount, setFrameCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check initial status
    checkHealth();
    
    // Listen for pose updates to count frames
    const handlePoseData = (data) => {
      if (recording && data.type === 'pose_update') {
        setFrameCount(prev => prev + 1);
      }
    };

    websocketService.addListener(handlePoseData);

    return () => {
      websocketService.removeListener(handlePoseData);
    };
  }, [recording]);

  const checkHealth = async () => {
    try {
      const health = await api.healthCheck();
      setCameraActive(health.camera_active);
      setRecording(health.recording);
      
      if (onStatusChange) {
        onStatusChange({ cameraActive: health.camera_active, recording: health.recording });
      }
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const handleStartCamera = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await api.startCamera(0, 0.3);
      websocketService.connect();
      setCameraActive(true);
      
      if (onStatusChange) {
        onStatusChange({ cameraActive: true, recording });
      }
    } catch (err) {
      setError('Failed to start camera: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStopCamera = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await api.stopCamera();
      websocketService.disconnect();
      setCameraActive(false);
      
      if (recording) {
        await handleStopRecording();
      }
      
      if (onStatusChange) {
        onStatusChange({ cameraActive: false, recording: false });
      }
    } catch (err) {
      setError('Failed to stop camera: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartRecording = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await api.startRecording(30);
      setRecording(true);
      setSessionId(result.session_id);
      setFrameCount(0);
      
      if (onStatusChange) {
        onStatusChange({ cameraActive, recording: true, sessionId: result.session_id });
      }
    } catch (err) {
      setError('Failed to start recording: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStopRecording = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await api.stopRecording();
      setRecording(false);
      
      if (onStatusChange) {
        onStatusChange({ 
          cameraActive, 
          recording: false, 
          lastRecording: result 
        });
      }
    } catch (err) {
      setError('Failed to stop recording: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="controls">
      <h3>Controls</h3>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <div className="control-group">
        <h4>Camera</h4>
        <div className="button-group">
          {!cameraActive ? (
            <button
              onClick={handleStartCamera}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Starting...' : 'Start Camera'}
            </button>
          ) : (
            <button
              onClick={handleStopCamera}
              disabled={loading}
              className="btn btn-danger"
            >
              {loading ? 'Stopping...' : 'Stop Camera'}
            </button>
          )}
        </div>
        <div className={`status-indicator ${cameraActive ? 'active' : ''}`}>
          {cameraActive ? '● Camera Active' : '○ Camera Inactive'}
        </div>
      </div>

      <div className="control-group">
        <h4>Recording</h4>
        <div className="button-group">
          {!recording ? (
            <button
              onClick={handleStartRecording}
              disabled={loading || !cameraActive}
              className="btn btn-success"
            >
              {loading ? 'Starting...' : 'Start Recording'}
            </button>
          ) : (
            <button
              onClick={handleStopRecording}
              disabled={loading}
              className="btn btn-warning"
            >
              {loading ? 'Stopping...' : 'Stop Recording'}
            </button>
          )}
        </div>
        <div className={`status-indicator ${recording ? 'recording' : ''}`}>
          {recording ? `🔴 Recording (${frameCount} frames)` : '○ Not Recording'}
        </div>
        {sessionId && (
          <div className="session-info">
            Session: {sessionId.substring(0, 8)}...
          </div>
        )}
      </div>
    </div>
  );
};

export default Controls;
