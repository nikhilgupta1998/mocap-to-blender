# Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **Webcam or camera device**
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nikhilgupta1998/mocap-to-blender.git
cd mocap-to-blender
```

### 2. Backend Setup

#### Create Virtual Environment

**On macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework
- Uvicorn - ASGI server
- MediaPipe - Pose detection
- OpenCV - Camera handling
- NumPy, SciPy - Numerical computing
- Pydantic - Data validation
- WebSockets - Real-time communication

#### Verify Installation

```bash
python -c "import mediapipe; import cv2; print('Backend dependencies OK')"
```

### 3. Frontend Setup

#### Navigate to Frontend

```bash
cd ../frontend
```

#### Install Dependencies

```bash
npm install
```

This will install:
- React - UI framework
- Three.js - 3D visualization
- Vite - Build tool
- Axios - HTTP client
- React Three Fiber - React renderer for Three.js

#### Verify Installation

```bash
npm run build
```

## Running the Application

### Start Backend Server

In the `backend` directory with virtual environment activated:

```bash
python app.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The backend API is now running at `http://localhost:8000`

### Start Frontend Development Server

In a new terminal, navigate to `frontend` directory:

```bash
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

The frontend is now running at `http://localhost:3000`

### Access the Application

Open your web browser and navigate to:
```
http://localhost:3000
```

## Configuration

### Camera Settings

By default, the application uses camera ID 0. If you have multiple cameras, you can change this:

1. In the frontend UI, look for camera settings
2. Or modify the default in `backend/app.py`:
   ```python
   camera = cv2.VideoCapture(0)  # Change 0 to your camera ID
   ```

### Smoothing Settings

Adjust smoothing strength in the camera start request:

```javascript
// In frontend/src/services/api.js
startCamera: async (cameraId = 0, smoothingAlpha = 0.3)
```

- **smoothingAlpha**: 0.1 (very smooth, more lag) to 0.9 (less smooth, less lag)
- **Recommended**: 0.3 for balanced smoothing

### Performance Settings

For better performance on slower machines:

**In `backend/pose_detector.py`:**
```python
self.pose = self.mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0  # Change from 1 to 0 for faster processing
)
```

**Model Complexity:**
- 0: Fastest, least accurate
- 1: Balanced (default)
- 2: Slowest, most accurate

## Troubleshooting

### Camera Not Found

**Error:** "Failed to open camera"

**Solutions:**
1. Check camera is connected
2. Try different camera ID (0, 1, 2, etc.)
3. Grant camera permissions in browser
4. Close other applications using the camera
5. On Linux, check user is in `video` group:
   ```bash
   sudo usermod -a -G video $USER
   ```

### Port Already in Use

**Error:** "Address already in use"

**Solutions:**

**Backend (port 8000):**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /F /PID <PID>  # Windows
```

**Frontend (port 3000):**
```bash
# Change port in vite.config.js
server: {
  port: 3001  # Use different port
}
```

### Module Not Found

**Error:** "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### MediaPipe Installation Issues

**On macOS ARM (M1/M2):**
```bash
# Install with specific build
pip install mediapipe --no-binary mediapipe
```

**On Linux:**
```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install -y python3-opencv
pip install mediapipe
```

### Low FPS / Performance Issues

**Solutions:**
1. Reduce camera resolution
2. Lower model complexity (see Performance Settings above)
3. Close other applications
4. Disable browser extensions
5. Use a dedicated GPU if available

### WebSocket Connection Failed

**Error:** "WebSocket connection failed"

**Solutions:**
1. Ensure backend is running
2. Check firewall settings
3. Verify proxy settings in `vite.config.js`
4. Try direct connection instead of proxy

## Development Tips

### Backend Development

Watch for file changes and auto-reload:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

Vite automatically hot-reloads on file changes. No additional configuration needed.

### Testing API Endpoints

Use curl or Postman to test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Start camera
curl -X POST http://localhost:8000/api/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 0, "smoothing_alpha": 0.3}'
```

## Production Deployment

### Backend

Use a production ASGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

Build for production:

```bash
npm run build
```

Serve the `dist` folder with a web server like Nginx or Apache.

### Security Considerations

1. **CORS**: Configure specific origins in `app.py`
2. **HTTPS**: Use SSL certificates in production
3. **Authentication**: Add authentication for API endpoints
4. **Rate Limiting**: Implement rate limiting
5. **File Size Limits**: Set limits on recording duration/size

## Next Steps

1. Read [API.md](API.md) for API documentation
2. Read [FORMATS.md](FORMATS.md) for export format details
3. Try recording a short motion
4. Export and import into Blender
5. Experiment with different smoothing settings

## Getting Help

- Check existing issues on GitHub
- Read the FAQ section
- Join the community discussions
- Submit a bug report with logs

## System Requirements

### Minimum

- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- GPU: Integrated graphics
- Camera: 640x480 @ 30 FPS
- Storage: 500 MB free space

### Recommended

- CPU: Quad-core 2.5 GHz or better
- RAM: 8 GB or more
- GPU: Dedicated graphics card
- Camera: 1280x720 @ 60 FPS
- Storage: 2 GB free space
