import threading
from loguru import logger
from ..extensions import socketio
from .state import active_tests, test_locks

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
