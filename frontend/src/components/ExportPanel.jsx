import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const ExportPanel = ({ lastRecording }) => {
  const [recordings, setRecordings] = useState([]);
  const [selectedRecording, setSelectedRecording] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecordings();
  }, [lastRecording]);

  const loadRecordings = async () => {
    try {
      const data = await api.listRecordings();
      setRecordings(data);
      
      // Auto-select the most recent recording
      if (data.length > 0 && !selectedRecording) {
        setSelectedRecording(data[0].session_id);
      }
    } catch (err) {
      console.error('Failed to load recordings:', err);
    }
  };

  const handleExport = async (format) => {
    if (!selectedRecording) {
      setError('Please select a recording to export');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let blob;
      let filename;

      if (format === 'bvh') {
        blob = await api.exportBVH(selectedRecording);
        filename = `${selectedRecording}.bvh`;
      } else if (format === 'blender') {
        blob = await api.exportBlender(selectedRecording);
        filename = `${selectedRecording}.py`;
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this recording?')) {
      return;
    }

    try {
      await api.deleteRecording(sessionId);
      await loadRecordings();
      
      if (selectedRecording === sessionId) {
        setSelectedRecording(null);
      }
    } catch (err) {
      setError('Failed to delete recording: ' + err.message);
    }
  };

  return (
    <div className="export-panel">
      <h3>Export & Recordings</h3>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="recordings-list">
        <h4>Available Recordings</h4>
        {recordings.length === 0 ? (
          <p className="no-recordings">No recordings available</p>
        ) : (
          <div className="recording-items">
            {recordings.map((rec) => (
              <div
                key={rec.session_id}
                className={`recording-item ${selectedRecording === rec.session_id ? 'selected' : ''}`}
                onClick={() => setSelectedRecording(rec.session_id)}
              >
                <div className="recording-info">
                  <div className="recording-id">
                    {rec.session_id.substring(0, 8)}...
                  </div>
                  <div className="recording-details">
                    {rec.frame_count} frames • {rec.duration.toFixed(1)}s • {rec.fps} FPS
                  </div>
                  <div className="recording-timestamp">
                    {new Date(rec.timestamp).toLocaleString()}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(rec.session_id);
                  }}
                  className="btn btn-small btn-danger"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="export-actions">
        <h4>Export Format</h4>
        <div className="button-group">
          <button
            onClick={() => handleExport('bvh')}
            disabled={!selectedRecording || loading}
            className="btn btn-primary"
          >
            {loading ? 'Exporting...' : 'Export as BVH'}
          </button>
          <button
            onClick={() => handleExport('blender')}
            disabled={!selectedRecording || loading}
            className="btn btn-primary"
          >
            {loading ? 'Exporting...' : 'Export as Blender Script'}
          </button>
        </div>
        <div className="export-info">
          <p><strong>BVH:</strong> Industry standard motion capture format</p>
          <p><strong>Blender Script:</strong> Python script for direct import into Blender</p>
        </div>
      </div>
    </div>
  );
};

export default ExportPanel;
