# API Documentation

## Base URL

```
http://localhost:8000
```

## Health Check

### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "camera_active": false,
  "recording": false
}
```

## Camera Endpoints

### POST /api/camera/start

Start the camera feed and pose detection.

**Request Body:**
```json
{
  "camera_id": 0,
  "smoothing_alpha": 0.3
}
```

**Parameters:**
- `camera_id` (int): Camera device ID (default: 0)
- `smoothing_alpha` (float): Smoothing factor 0-1 (default: 0.3, lower = smoother)

**Response:**
```json
{
  "status": "started",
  "camera_id": 0,
  "smoothing_alpha": 0.3
}
```

### POST /api/camera/stop

Stop the camera feed.

**Response:**
```json
{
  "status": "stopped"
}
```

## WebSocket

### WS /ws/pose

WebSocket endpoint for real-time pose data streaming.

**Message Format:**
```json
{
  "type": "pose_update",
  "data": {
    "landmarks": [
      {
        "x": 0.5,
        "y": 0.3,
        "z": -0.2,
        "visibility": 0.98
      }
    ],
    "world_landmarks": [...],
    "timestamp": 1234567890.123
  }
}
```

**Error Message:**
```json
{
  "type": "error",
  "message": "Failed to capture frame"
}
```

## Recording Endpoints

### POST /api/recording/start

Start a new recording session.

**Request Body:**
```json
{
  "fps": 30.0
}
```

**Response:**
```json
{
  "status": "recording",
  "session_id": "uuid-here",
  "fps": 30.0
}
```

### POST /api/recording/stop

Stop the current recording session.

**Response:**
```json
{
  "status": "stopped",
  "session_id": "uuid-here",
  "frame_count": 300,
  "duration": 10.0
}
```

### GET /api/recording/{session_id}

Get a specific recording by session ID.

**Response:**
```json
{
  "metadata": {
    "session_id": "uuid-here",
    "fps": 30.0,
    "duration": 10.0,
    "frame_count": 300,
    "timestamp": "2026-02-06T10:30:00Z",
    "landmark_count": 33
  },
  "frames": [
    {
      "frame_id": 0,
      "timestamp": 0.0,
      "landmarks": [...],
      "world_landmarks": [...]
    }
  ]
}
```

### GET /api/recordings

List all available recordings.

**Response:**
```json
[
  {
    "session_id": "uuid-here",
    "fps": 30.0,
    "duration": 10.0,
    "frame_count": 300,
    "timestamp": "2026-02-06T10:30:00Z",
    "landmark_count": 33
  }
]
```

### DELETE /api/recording/{session_id}

Delete a recording.

**Response:**
```json
{
  "status": "deleted",
  "session_id": "uuid-here"
}
```

## Export Endpoints

### POST /api/export/bvh

Export a recording as BVH file.

**Request Body:**
```json
{
  "session_id": "uuid-here",
  "format": "bvh"
}
```

**Response:**
- File download of `.bvh` file

### POST /api/export/blender

Export a recording as Blender Python script.

**Request Body:**
```json
{
  "session_id": "uuid-here",
  "format": "blender"
}
```

**Response:**
- File download of `.py` file

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "No active recording session"
}
```

**404 Not Found:**
```json
{
  "detail": "Recording not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to open camera"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, consider adding rate limits to prevent abuse.

## CORS

CORS is enabled for all origins (`*`) in development. In production, configure specific origins.

## WebSocket Connection

To connect to the WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/pose');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'pose_update') {
    // Handle pose data
    console.log(data.data.landmarks);
  }
};
```

The WebSocket will automatically send pose updates at ~30 FPS when camera is active.
