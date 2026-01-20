"""
Flask Backend API for Local AI Testing Platform
Supports Mobile (Appium) and Web (Playwright) Agents
"""
from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import os
import yaml
import threading
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
import json
import time
import traceback
from loguru import logger

# Fix for missing ANDROID_HOME environment variable
if not os.environ.get('ANDROID_HOME'):
    # Common Default Paths for Windows
    possible_paths = [
        r'C:\Users\hasib\AppData\Local\Android\Sdk',  # Specific user path found
        os.path.expanduser('~\\AppData\\Local\\Android\\Sdk'),  # Generic user path
        r'C:\Program Files\Android\Android Studio\plugins\android\lib\sdk' # Another common path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['ANDROID_HOME'] = path
            logger.info(f"Automatically set ANDROID_HOME to: {path}")
            
            # Also add platform-tools and emulator to PATH if not present
            updates = [
                os.path.join(path, 'platform-tools'),
                os.path.join(path, 'emulator'),
                os.path.join(path, 'tools'),
                os.path.join(path, 'build-tools') # Just the root, specific versions might be hard to guess
            ]
            
            current_path = os.environ.get('PATH', '')
            for update in updates:
                if os.path.exists(update) and update not in current_path:
                    os.environ['PATH'] = update + os.pathsep + current_path
            
            break

    if not os.environ.get('ANDROID_HOME'):
         logger.warning("ANDROID_HOME not found in common locations. Please set it manually.")

# Import Mobile Agent Modules
from agents.mobile.emulator_manager import EmulatorManager
from agents.mobile.apk_installer import APKInstaller
from agents.mobile.ui_explorer import UIExplorer
from agents.mobile.report_generator import ReportGenerator

# Import Web Agent Module
from agents.web.web_agent import WebTestingAgent

# Import enhanced AI agent if available
try:
    from agents.mobile.ai_agent_core import AITestingAgent
    from agents.mobile.ai_test_executor import AITestExecutor
    AI_AVAILABLE = True
except ImportError:
    logger.warning("Mobile AI modules not found, will use basic testing")
    AI_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
SCREENSHOTS_FOLDER = 'screenshots'
ALLOWED_EXTENSIONS = {'apk'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Create necessary folders
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(REPORTS_FOLDER).mkdir(exist_ok=True)
Path(SCREENSHOTS_FOLDER).mkdir(exist_ok=True)

# Store active test sessions
active_tests = {}
test_locks = {}

def load_config():
    """Load config from YAML"""
    try:
        config_path = 'config/config.yaml'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
             logger.warning("Config file not found, using defaults")
             return _get_default_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return _get_default_config()

def _get_default_config():
    return {
        'adb': {'device_id': 'emulator-5554'},
        'emulator': {'name': 'Pixel_6_API_34', 'port': 5554, 'wait_timeout': 120},
        'testing': {
            'max_exploration_depth': 10,
            'max_clicks_per_screen': 5,
            'screenshot_delay': 2
        },
        'report': {
            'output_dir': 'reports',
            'screenshot_dir': 'screenshots',
            'format': 'html'
        },
        'logging': {
            'level': 'INFO',
            'file': 'testing_agent.log'
        },
        'exploration': {'strategy': 'hybrid'}
    }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'Local AI Testing Platform API is running',
        'ai_available': AI_AVAILABLE,
        'active_tests': len(active_tests)
    })

@app.route('/api/upload', methods=['POST'])
def upload_apk():
    """Upload APK file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .apk files allowed'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        logger.info(f"APK uploaded: {filename} (Session: {session_id})")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename,
            'filepath': filepath
        })
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# MOBILE TESTING ENDPOINTS
# ==========================================

def gen_frames():
    """Video streaming generator function."""
    config = _get_default_config()
    device_id = config.get('adb', {}).get('device_id', 'emulator-5554')
    
    while True:
        try:
             # Fast screenshot using exec-out screencap -p (PNG format really, but often works as MJPEG source if valid image headers)
             # Actually screencap -p is PNG. MJPEG usually expects JPEG. 
             # Let's try to pass it anyway or stream raw. 
             # Creating a proper MJPEG stream without conversion might be tricky if browser expects JPEG.
             # PNG is supported in multipart/x-mixed-replace by most browsers.
             
             process = subprocess.Popen(
                 ['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], 
                 stdout=subprocess.PIPE, 
                 stderr=subprocess.PIPE
             )
             frame, _ = process.communicate()
             if frame:
                 yield (b'--frame\r\n'
                        b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
             
             time.sleep(0.1)
        except Exception:
             time.sleep(1)

@app.route('/video_feed/<session_id>')
def video_feed(session_id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/mobile/start', methods=['POST'])
def start_mobile_test():
    """Start AI-powered mobile testing"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        test_mode = data.get('test_mode', 'auto')
        credentials = data.get('credentials', {})
        test_context = data.get('test_context', '')
        ai_instructions = data.get('ai_instructions', '')
        apk_filepath = data.get('apk_filepath')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id parameter'}), 400
        
        # Handle APK finding logic if path not provided
        if not apk_filepath:
            upload_files = os.listdir(UPLOAD_FOLDER)
            matching_files = [f for f in upload_files if f.startswith(session_id)]
            
            if not matching_files:
                return jsonify({'error': 'APK file not found. Please upload the APK first.'}), 404
            
            apk_filepath = os.path.join(UPLOAD_FOLDER, matching_files[0])
        
        if not os.path.exists(apk_filepath):
             return jsonify({'error': f'APK file not found at path: {apk_filepath}'}), 404

        if session_id in active_tests and active_tests[session_id]['status'] == 'running':
            return jsonify({'error': 'Test already running for this session'}), 400
        
        # Initialize test session
        active_tests[session_id] = {
            'type': 'mobile',
            'status': 'initializing',
            'progress': 0,
            'message': 'Preparing mobile test environment...',
            'results': None,
            'error': None,
            'created_at': time.time(),
            'apk_filepath': apk_filepath
        }
        
        test_locks[session_id] = threading.Lock()
        
        thread = threading.Thread(
            target=run_mobile_test_logic,
            args=(session_id, apk_filepath, test_mode, credentials, test_context, ai_instructions),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Mobile test started successfully'
        })
        
    except Exception as e:
        logger.error(f"Start mobile test error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_mobile_test_logic(session_id, apk_filepath, test_mode, credentials, test_context, ai_instructions):
    """Run Mobile AI testing in background"""
    try:
        update_test_status(session_id, 'running', 10, 'Loading configuration...')
        config = load_config()
        
        # Initialize components
        update_test_status(session_id, progress=20, message='Initializing components...')
        emulator = EmulatorManager(config)
        apk_installer = APKInstaller(config)
        ui_explorer = UIExplorer(config)
        report_generator = ReportGenerator(config)
        
        update_test_status(session_id, progress=30, message='Initializing AI agent...')
        
        if AI_AVAILABLE:
            # Force strict API key usage
            gemini_api_key = 'AIzaSyDeET9gqOoeQ1Kb84LZEC5dhsm6Tm7fUN4'
            ai_agent = AITestingAgent(config, gemini_api_key)
            
            if test_mode == 'guided' and test_context:
                ai_agent.app_context['user_context'] = test_context
            if test_mode == 'custom' and ai_instructions:
                ai_agent.app_context['custom_instructions'] = ai_instructions
            if credentials.get('hasLogin') and credentials.get('username'):
                ai_agent.app_context['credentials'] = credentials
            
            # Define callback for granular updates
            def log_callback(message):
                update_test_status(session_id, message=message)
            
            test_executor = AITestExecutor(config, ui_explorer, apk_installer, ai_agent, status_callback=log_callback)
        else:
            from agents.mobile.test_executor import TestExecutor
            test_executor = TestExecutor(config, ui_explorer, apk_installer)
        
        # Check/Start emulator
        update_test_status(session_id, progress=40, message='Checking emulator...')
        if not emulator.is_running():
            update_test_status(session_id, message='Starting Android emulator...')
            if not emulator.start():
                raise Exception("Failed to start emulator.")
        
        # Install APK
        update_test_status(session_id, progress=50, message='Installing APK...')
        if not apk_installer.install(apk_filepath):
            raise Exception("Failed to install APK.")
        
        # Run tests
        update_test_status(session_id, progress=60, message='AI testing in progress...')
        test_summary = test_executor.run_tests()
        
        # Generate report
        update_test_status(session_id, progress=90, message='Generating report...')
        apk_info = {
            'package_name': apk_installer.package_name,
            'main_activity': apk_installer.main_activity,
            'apk_path': apk_filepath
        }
        report_path = report_generator.generate(test_summary, apk_info)
        
        apk_installer.stop()
        
        duration = time.time() - active_tests[session_id]['created_at']
        duration_str = f"{int(duration // 60)}m {int(duration % 60)}s"
        
        results = {
            'total_tests': test_summary['total_tests'],
            'passed': test_summary['passed'],
            'failed': test_summary['failed'],
            'screens_explored': test_summary['screens_explored'],
            'report_path': report_path,
            'ai_insights': test_summary.get('ai_insights', 'AI insights not available'),
            'duration': duration_str
        }
        
        update_test_status(session_id, 'completed', 100, 'Mobile testing completed!', results=results)
        
    except Exception as e:
        logger.error(f"Mobile test failed: {e}")
        update_test_status(session_id, 'failed', message=f"Error: {str(e)}", error=str(e))

# ==========================================
# WEB TESTING ENDPOINTS
# ==========================================

@app.route('/api/web/start', methods=['POST'])
def start_web_test():
    """Start AI-powered web testing"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') or str(uuid.uuid4())
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'Missing URL parameter'}), 400

        if session_id in active_tests and active_tests[session_id]['status'] == 'running':
             return jsonify({'error': 'Test already running for this session'}), 400

        active_tests[session_id] = {
            'type': 'web',
            'status': 'initializing',
            'progress': 0,
            'message': 'Preparing web test...',
            'results': None,
            'error': None,
            'created_at': time.time(),
            'url': url
        }
        
        test_locks[session_id] = threading.Lock()
        
        thread = threading.Thread(
            target=run_web_test_logic,
            args=(session_id, url),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True, 
            'session_id': session_id,
            'message': 'Web test started successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_web_test_logic(session_id, url):
    """Run Web testing using Playwright"""
    try:
        update_test_status(session_id, 'running', 10, f'Connecting to {url}...')
        
        agent = WebTestingAgent(headless=False) # Run headless=False so user can see or maybe True is better for background. User said "headless" in requirements. "launches a local headless browser". Okay, I set headless=True in default init, but passed False here. Let's pass True.
        
        # Re-init agent with headless=True as per requirements
        agent = WebTestingAgent(headless=True)
        
        update_test_status(session_id, 'running', 30, 'Scanning DOM and checking for issues...')
        
        results = agent.run_test(url)
        
        if results['status'] == 'completed':
             update_test_status(session_id, 'completed', 100, 'Web testing completed!', results=results)
        else:
             update_test_status(session_id, 'failed', message=f"Web test failed: {results.get('error')}", error=results.get('error'))
            
    except Exception as e:
        logger.error(f"Web test failed: {e}")
        update_test_status(session_id, 'failed', message=f"Error: {str(e)}", error=str(e))


# ==========================================
# COMMON UTILS
# ==========================================

def update_test_status(session_id, status=None, progress=None, message=None, results=None, error=None):
    """Thread-safe status update"""
    if session_id in test_locks:
        with test_locks[session_id]:
            if status: active_tests[session_id]['status'] = status
            if progress is not None: active_tests[session_id]['progress'] = progress
            if message: active_tests[session_id]['message'] = message
            if results: active_tests[session_id]['results'] = results
            if error: active_tests[session_id]['error'] = error
            
            # Emit SocketIO event
            try:
                socketio.emit('test_update', {
                    'session_id': session_id,
                    'status': active_tests[session_id].get('status'),
                    'progress': active_tests[session_id].get('progress'),
                    'message': active_tests[session_id].get('message'),
                    'results': active_tests[session_id].get('results'),
                    'error': active_tests[session_id].get('error')
                })
            except Exception as e:
                logger.error(f"Socket emit failed: {e}")

@app.route('/api/test/status/<session_id>', methods=['GET'])
def get_test_status(session_id):
    if session_id not in active_tests:
        return jsonify({'error': 'Session not found'}), 404
    with test_locks.get(session_id, threading.Lock()):
        status_data = active_tests[session_id].copy()
    return jsonify(status_data)

@app.route('/api/report/<session_id>', methods=['GET'])
def download_report(session_id):
    # Same logic as before, extended for web if needed (web returns JSON results primarily, mobile has HTML)
    if session_id not in active_tests: return jsonify({'error': 'Session not found'}), 404
    test_data = active_tests[session_id]
    
    if test_data['type'] == 'mobile':
        report_path = test_data.get('results', {}).get('report_path')
        if report_path and os.path.exists(report_path):
             return send_file(report_path, as_attachment=True)
    
    return jsonify({'error': 'Report not available'}), 404

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    sessions = []
    for sid, data in active_tests.items():
        sessions.append({
            'session_id': sid,
            'type': data.get('type', 'unknown'),
            'status': data['status'],
            'progress': data['progress'],
            'message': data['message'],
            'created_at': data.get('created_at', 0)
        })
    sessions.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'sessions': sessions})

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOTS_FOLDER, filename)

@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    if session_id in active_tests:
        del active_tests[session_id]
        if session_id in test_locks: del test_locks[session_id]
    return jsonify({'success': True})

if __name__ == '__main__':
    logger.add("api_server.log", rotation="10 MB", level="DEBUG")
    logger.info("Starting Local AI Testing Platform API")
    # Disable reloader to prevent restarts when screenshots/reports are generated
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=5000)
