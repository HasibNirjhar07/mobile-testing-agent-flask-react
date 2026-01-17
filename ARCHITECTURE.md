# Mobile AI Testing w/ Cloud Streaming Architecture

## 1. Overview
This system enables users to upload APKs, run them on a remote Android environment (Dockerized Emulator), and view the test execution in real-time via the web dashboard. The core innovation is "live streaming" the emulator state and "pushing" AI logic logs to the frontend using WebSockets.

## 2. Infrastructure Architecture (Cloud/Docker)

### A. Emulator Hosting
Instead of running on the API server host directly, emulators should be containerized.
*   **Container**: `us-docker.pkg.dev/android-emulator-images/images/r-google-atd-x86-64` (Google's official emulator image) or `budtmo/docker-android`.
*   **Orchestration**: Kubernetes (K8s) or Docker Compose.
*   **Lifecycle**:
    1.  API receives upload.
    2.  API spins up a new `Pod`/`Container` for that session.
    3.  Container exposes ADB port (5555) and potentially a WebRTC/VNC port.

### B. Screen Streaming
We need to get pixels from the Android container to the React frontend.
**Approaches:**
1.  **WebRTC (Low Latency < 200ms)**:
    *   Use `scrcpy` server inside the container.
    *   Forward H.264 stream to a `mediamtx` or `janus-gateway`.
    *   Frontend consumes via `<video>` tag (WebRTC).
2.  **MJPEG via Websocket (Medium Latency ~500ms - Easiest for "Now")**:
    *   Backend continuously runs `adb exec-out screencap -p`.
    *   Encodes frame to JPEG.
    *   Sends to frontend via Flask route `/video_feed`.
3.  **VNC/noVNC (High Latency)**:
    *   Run a VNC server on Android.
    *   Use `novnc.js` on frontend.

### C. Backend Architecture (Flask + SocketIO)
*   **API Server**: Handles uploads, session mgmt.
*   **Worker Threads**:
    *   `TestExecutor`: Runs the AI agents (Gemini/Appium).
    *   `Streamer`: Captures screenshots -> Queue -> MJPEG Stream.
*   **Communication**:
    *   `Flask-SocketIO`: Pushes logs (Move A -> Click B -> Validating C) and status updates.

## 3. Frontend Architecture (React)
*   **Components**:
    *   `LiveEmulator`: An `<img>` tag ref that updates `src` or connects to MJPEG stream.
    *   `LogConsole`: A scrolling list of events received via SocketIO.
    *   `TestStatus`: Real-time stats (Pass/Fail).

## 4. Implementation Steps (Current "Local Cloud" Version)

Since we are running on a single Windows host for now, we will simulate the cloud stack:

1.  **Streaming**: Implement an endpoint `/api/stream/<session_id>` that yields multipart MJPEG frames captured via ADB.
2.  **Real-Time Logs**: Replace polling `active_tests` with `socket.on('test_update')`.
3.  **Dashboard**: Embed the stream and log console.

## 5. Security & Scalability
*   **Security**: Sandbox emulators in containers. One container per session. Kill after timeout.
*   **Scalability**: Use queue (Celery/Redis) to manage waiting list of tests if emulator slots are full.
