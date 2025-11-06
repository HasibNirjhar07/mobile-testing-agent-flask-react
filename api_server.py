"""
Flask Backend API for AI Mobile Testing Web Interface
Complete and Production-Ready
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
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

# Import your existing testing modules
from app.emulator_manager import EmulatorManager
from app.apk_installer import APKInstaller
from app.ui_explorer import UIExplorer
from app.report_generator import ReportGenerator

# Import enhanced AI agent if available
try:
    from app.ai_agent_core import AITestingAgent
    from app.ai_test_executor import AITestExecutor
    AI_AVAILABLE = True
except ImportError:
    logger.warning("AI modules not found, will use basic testing")
    AI_AVAILABLE = False

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
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
        with open('config/config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        # Return default config
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
        'message': 'AI Mobile Testing Agent API is running',
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

@app.route('/api/test/start', methods=['POST'])
def start_test():
    """Start AI-powered testing"""
    try:
        data = request.get_json()
        
        session_id = data.get('session_id')
        test_mode = data.get('test_mode', 'auto')
        credentials = data.get('credentials', {})
        test_context = data.get('test_context', '')
        ai_instructions = data.get('ai_instructions', '')

        print(test_context)
        print(ai_instructions)
        
        # Try to get apk_filepath from request, or construct it from session_id
        apk_filepath = data.get('apk_filepath')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id parameter'}), 400
        
        # If apk_filepath not provided, try to find it based on session_id
        if not apk_filepath:
            upload_files = os.listdir(UPLOAD_FOLDER)
            matching_files = [f for f in upload_files if f.startswith(session_id)]
            
            if not matching_files:
                return jsonify({'error': 'APK file not found. Please upload the APK first.'}), 404
            
            apk_filepath = os.path.join(UPLOAD_FOLDER, matching_files[0])
            logger.info(f"Found APK file: {apk_filepath}")
        
        # Check if APK file exists
        if not os.path.exists(apk_filepath):
            logger.error(f"APK file not found at: {apk_filepath}")
            return jsonify({'error': f'APK file not found at path: {apk_filepath}'}), 404
        
        # Check if test already running
        if session_id in active_tests and active_tests[session_id]['status'] == 'running':
            return jsonify({'error': 'Test already running for this session'}), 400
        
        # Initialize test session
        active_tests[session_id] = {
            'status': 'initializing',
            'progress': 0,
            'message': 'Preparing test environment...',
            'results': None,
            'error': None,
            'created_at': time.time(),
            'apk_filepath': apk_filepath  # Store for reference
        }
        
        test_locks[session_id] = threading.Lock()
        
        # Start testing in background thread
        thread = threading.Thread(
            target=run_ai_test,
            args=(session_id, apk_filepath, test_mode, credentials, test_context, ai_instructions),
            daemon=True
        )
        
        thread.start()
        
        logger.info(f"Test started for session: {session_id} with APK: {apk_filepath}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Test started successfully',
            'apk_filepath': apk_filepath
        })
    
    except Exception as e:
        logger.error(f"Start test error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def update_test_status(session_id, status=None, progress=None, message=None, results=None, error=None):
    """Thread-safe status update"""
    if session_id in test_locks:
        with test_locks[session_id]:
            if status:
                active_tests[session_id]['status'] = status
            if progress is not None:
                active_tests[session_id]['progress'] = progress
            if message:
                active_tests[session_id]['message'] = message
            if results:
                active_tests[session_id]['results'] = results
            if error:
                active_tests[session_id]['error'] = error

def run_ai_test(session_id, apk_filepath, test_mode, credentials, test_context, ai_instructions):
    """Run AI testing in background"""
    try:
        # Update status
        update_test_status(session_id, 'running', 10, 'Loading configuration...')
        time.sleep(1)
        
        # Load config
        config = load_config()
        
        # Initialize components
        update_test_status(session_id, progress=20, message='Initializing testing components...')
        
        emulator = EmulatorManager(config)
        apk_installer = APKInstaller(config)
        ui_explorer = UIExplorer(config)
        report_generator = ReportGenerator(config)
        
        # Initialize AI agent if available
        update_test_status(session_id, progress=30, message='Initializing AI agent...')
        
        if AI_AVAILABLE:
            gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyC41RoUNUYb_q6hJERw99DJr3f-oz2OMRc')
            ai_agent = AITestingAgent(config, gemini_api_key)
            
            # Customize AI agent based on user input
            if test_mode == 'guided' and test_context:
                ai_agent.app_context['user_context'] = test_context
            
            if test_mode == 'custom' and ai_instructions:
                ai_agent.app_context['custom_instructions'] = ai_instructions
            
            if credentials.get('hasLogin') and credentials.get('username'):
                ai_agent.app_context['credentials'] = {
                    'username': credentials.get('username', ''),
                    'password': credentials.get('password', ''),
                    'email': credentials.get('email', '')
                }
            
            test_executor = AITestExecutor(config, ui_explorer, apk_installer, ai_agent)
        else:
            from app.test_executor import TestExecutor
            test_executor = TestExecutor(config, ui_explorer, apk_installer)
        
        # Check/Start emulator
        update_test_status(session_id, progress=40, message='Checking emulator status...')
        
        if not emulator.is_running():
            update_test_status(session_id, message='Starting Android emulator (this may take a few minutes)...')
            if not emulator.start():
                raise Exception("Failed to start emulator. Make sure Android emulator is configured.")
        
        # Install APK
        update_test_status(session_id, progress=50, message='Installing APK on emulator...')
        
        if not apk_installer.install(apk_filepath):
            raise Exception("Failed to install APK. Check if APK is valid and emulator is ready.")
        
        # Run tests
        update_test_status(session_id, progress=60, message='AI testing in progress - Exploring app...')
        
        test_summary = test_executor.run_tests()
        
        # Generate report
        update_test_status(session_id, progress=90, message='Generating test report...')
        
        apk_info = {
            'package_name': apk_installer.package_name,
            'main_activity': apk_installer.main_activity,
            'apk_path': apk_filepath
        }
        
        report_path = report_generator.generate(test_summary, apk_info)
        
        # Cleanup
        apk_installer.stop()
        
        # Calculate duration
        duration = time.time() - active_tests[session_id]['created_at']
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f"{minutes}m {seconds}s"
        
        # Update final status
        results = {
            'total_tests': test_summary['total_tests'],
            'passed': test_summary['passed'],
            'failed': test_summary['failed'],
            'screens_explored': test_summary['screens_explored'],
            'report_path': report_path,
            'ai_insights': test_summary.get('ai_insights', 'AI insights not available'),
            'duration': duration_str
        }
        
        update_test_status(
            session_id,
            status='completed',
            progress=100,
            message='Testing completed successfully!',
            results=results
        )
        
        logger.info(f"Test completed successfully for session: {session_id}")
        
    except Exception as e:
        error_msg = f'Error: {str(e)}'
        logger.error(f"Test failed for session {session_id}: {error_msg}")
        logger.error(traceback.format_exc())
        
        update_test_status(
            session_id,
            status='failed',
            message=error_msg,
            error=str(e)
        )

@app.route('/api/test/status/<session_id>', methods=['GET'])
def get_test_status(session_id):
    """Get current test status"""
    if session_id not in active_tests:
        return jsonify({'error': 'Session not found'}), 404
    
    # Return copy to avoid race conditions
    with test_locks.get(session_id, threading.Lock()):
        status_data = active_tests[session_id].copy()
    
    return jsonify(status_data)

@app.route('/api/report/<session_id>', methods=['GET'])
def download_report(session_id):
    """Download test report"""
    try:
        if session_id not in active_tests:
            return jsonify({'error': 'Session not found'}), 404
        
        test_data = active_tests[session_id]
        
        if test_data['status'] != 'completed':
            return jsonify({'error': 'Test not completed yet'}), 400
        
        report_path = test_data['results']['report_path']
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f'test_report_{session_id}.html'
        )
    
    except Exception as e:
        logger.error(f"Download report error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/view/<session_id>', methods=['GET'])
def view_report(session_id):
    """View report in browser"""
    try:
        if session_id not in active_tests:
            return jsonify({'error': 'Session not found'}), 404
        
        test_data = active_tests[session_id]
        
        if test_data['status'] != 'completed':
            return jsonify({'error': 'Test not completed yet'}), 400
        
        report_path = test_data['results']['report_path']
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        return send_file(report_path, mimetype='text/html')
    
    except Exception as e:
        logger.error(f"View report error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all test sessions"""
    sessions = []
    for session_id, data in active_tests.items():
        sessions.append({
            'session_id': session_id,
            'status': data['status'],
            'progress': data['progress'],
            'message': data['message'],
            'created_at': data.get('created_at', 0)
        })
    
    # Sort by creation time, newest first
    sessions.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'sessions': sessions})

@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """Clean up session data"""
    try:
        if session_id in active_tests:
            test_data = active_tests[session_id]
            
            # Delete APK file if exists
            apk_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(session_id)]
            for apk_file in apk_files:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, apk_file))
                except:
                    pass
            
            # Remove from active tests
            del active_tests[session_id]
            
            if session_id in test_locks:
                del test_locks[session_id]
        
        return jsonify({'success': True, 'message': 'Session cleaned up'})
    
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config = load_config()
        return jsonify({
            'success': True,
            'config': {
                'emulator': config.get('emulator', {}),
                'testing': config.get('testing', {}),
                'ai_available': AI_AVAILABLE
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve screenshots
@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Serve screenshot files"""
    return send_from_directory(SCREENSHOTS_FOLDER, filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Cleanup old sessions on startup
def cleanup_old_sessions():
    """Remove sessions older than 24 hours"""
    current_time = time.time()
    sessions_to_remove = []
    
    for session_id, data in active_tests.items():
        created_at = data.get('created_at', 0)
        if current_time - created_at > 86400:  # 24 hours
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        try:
            # Clean up files
            apk_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(session_id)]
            for apk_file in apk_files:
                os.remove(os.path.join(UPLOAD_FOLDER, apk_file))
            
            del active_tests[session_id]
            logger.info(f"Cleaned up old session: {session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")

if __name__ == '__main__':
    # Setup logging
    logger.add(
        "api_server.log",
        rotation="10 MB",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )
    
    logger.info("=" * 60)
    logger.info("AI Mobile Testing Agent - API Server")
    logger.info("=" * 60)
    logger.info(f"AI Available: {AI_AVAILABLE}")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"Reports folder: {REPORTS_FOLDER}")
    logger.info("Starting server on http://localhost:5000")
    logger.info("=" * 60)
    
    # Cleanup old sessions
    cleanup_old_sessions()
    
    # Run server
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)