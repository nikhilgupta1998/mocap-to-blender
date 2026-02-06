/**
 * API service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = '/api';

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await axios.get('/health');
    return response.data;
  },

  // Camera endpoints
  startCamera: async (cameraId = 0, smoothingAlpha = 0.3) => {
    const response = await axios.post(`${API_BASE_URL}/camera/start`, {
      camera_id: cameraId,
      smoothing_alpha: smoothingAlpha
    });
    return response.data;
  },

  stopCamera: async () => {
    const response = await axios.post(`${API_BASE_URL}/camera/stop`);
    return response.data;
  },

  // Recording endpoints
  startRecording: async (fps = 30) => {
    const response = await axios.post(`${API_BASE_URL}/recording/start`, {
      fps: fps
    });
    return response.data;
  },

  stopRecording: async () => {
    const response = await axios.post(`${API_BASE_URL}/recording/stop`);
    return response.data;
  },

  getRecording: async (sessionId) => {
    const response = await axios.get(`${API_BASE_URL}/recording/${sessionId}`);
    return response.data;
  },

  listRecordings: async () => {
    const response = await axios.get(`${API_BASE_URL}/recordings`);
    return response.data;
  },

  deleteRecording: async (sessionId) => {
    const response = await axios.delete(`${API_BASE_URL}/recording/${sessionId}`);
    return response.data;
  },

  // Export endpoints
  exportBVH: async (sessionId) => {
    const response = await axios.post(`${API_BASE_URL}/export/bvh`, {
      session_id: sessionId,
      format: 'bvh'
    }, {
      responseType: 'blob'
    });
    return response.data;
  },

  exportBlender: async (sessionId) => {
    const response = await axios.post(`${API_BASE_URL}/export/blender`, {
      session_id: sessionId,
      format: 'blender'
    }, {
      responseType: 'blob'
    });
    return response.data;
  }
};
