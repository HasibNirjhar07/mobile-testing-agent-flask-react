from flask import Blueprint, request, jsonify, send_file, send_from_directory, Response
import os
import time
import uuid
import threading
import subprocess
from werkzeug.utils import secure_filename
from loguru import logger

from ..core.config import config
from ..services.state import active_tests, test_locks
from ..services.runner import run_mobile_test_logic, run_web_test_logic

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'apk'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'AI Testing Platform API (Production Ready)',
        'active_tests': len(active_tests)
    })

@api_bp.route('/api/upload', methods=['POST'])
def upload_apk():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .apk files allowed'}), 400
        
        session_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = config.UPLOAD_FOLDER / f"{session_id}_{filename}"
        
        file.save(str(filepath))
        
        logger.info(f"APK uploaded: {filename} (Session: {session_id})")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename,
            'filepath': str(filepath)
        })
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_active_device():
    """Returns the first available device ID with 'device' status"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]
        for line in lines:
            if 'device' in line and 'unauthorized' not in line:
                return line.split('\t')[0]
    except Exception:
        pass
    return 'emulator-5554' # Fallback

def gen_frames(session_id):
    device_id = get_active_device()
    logger.info(f"Streaming from device: {device_id}")
    while True:
        try:
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

@api_bp.route('/video_feed/<session_id>')
def video_feed(session_id):
    return Response(gen_frames(session_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@api_bp.route('/api/mobile/start', methods=['POST'])
def start_mobile_test():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        test_mode = data.get('test_mode', 'auto')
        credentials = data.get('credentials', {})
        test_context = data.get('test_context', '')
        ai_instructions = data.get('ai_instructions', '')
        apk_filepath = data.get('apk_filepath')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id'}), 400

        if session_id in active_tests and active_tests[session_id]['status'] == 'running':
            return jsonify({'error': 'Test already running'}), 400
            
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
        logger.error(f"Start error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/web/start', methods=['POST'])
def start_web_test():
    try:
        data = request.get_json()
        session_id = data.get('session_id') or str(uuid.uuid4())
        url = data.get('url')
        if not url: return jsonify({'error': 'Missing URL'}), 400
        active_tests[session_id] = {
            'type': 'web',
            'status': 'initializing',
            'progress': 0,
            'message': 'Preparing web test...',
            'created_at': time.time()
        }
        test_locks[session_id] = threading.Lock()
        thread = threading.Thread(target=run_web_test_logic, args=(session_id, url), daemon=True)
        thread.start()
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/test/status/<session_id>', methods=['GET'])
def get_status(session_id):
    if session_id not in active_tests: return jsonify({'error': 'Session not found'}), 404
    return jsonify(active_tests[session_id])

@api_bp.route('/api/report/<session_id>', methods=['GET'])
def download_report(session_id):
    if session_id not in active_tests: return jsonify({'error': 'Session not found'}), 404
    test_data = active_tests[session_id]
    if test_data['type'] == 'mobile':
        report_path = test_data.get('results', {}).get('report_path')
        if report_path and os.path.exists(report_path):
             return send_file(report_path, as_attachment=True)
    return jsonify({'error': 'Report not available'}), 404

@api_bp.route('/api/sessions', methods=['GET'])
def list_sessions():
    sessions = []
    for sid, data in active_tests.items():
        sessions.append({
            'session_id': sid,
            'type': data.get('type', 'unknown'),
            'status': data.get('status'),
            'progress': data.get('progress'),
            'message': data.get('message'),
            'created_at': data.get('created_at', 0)
        })
    sessions.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'sessions': sessions})

@api_bp.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    return send_from_directory(config.SCREENSHOT_FOLDER, filename)
