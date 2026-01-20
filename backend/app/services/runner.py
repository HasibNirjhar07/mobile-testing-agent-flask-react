import os
import time
import threading
from loguru import logger
import yaml

from ..core.config import config
from ..services.test_manager import update_test_status
from ..services.state import active_tests

# Import Agent Modules
try:
    from ..agents.mobile.emulator_manager import EmulatorManager
    from ..agents.mobile.apk_installer import APKInstaller
    from ..agents.mobile.ui_explorer import UIExplorer
    from ..agents.mobile.report_generator import ReportGenerator
    from ..agents.web.web_agent import WebTestingAgent
except ImportError as e:
    logger.error(f"Import Error: {e}")

# Import AI Agent
try:
    from ..agents.mobile.ai_agent_core import AITestingAgent
    from ..agents.mobile.ai_test_executor import AITestExecutor
    AI_AVAILABLE = True
except ImportError:
    logger.warning("Mobile AI modules not found")
    AI_AVAILABLE = False

def load_config_yaml():
    """Load config from YAML"""
    try:
        # config.BASE_DIR is '.../backend'
        config_path = config.BASE_DIR / 'app' / 'config' / 'config.yaml'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
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
            'screenshot_delay': 2
        },
        'report': {'output_dir': 'reports'},
        'exploration': {'strategy': 'hybrid'}
    }

def run_mobile_test_logic(session_id, apk_filepath, test_mode, credentials, test_context, ai_instructions):
    """Run Mobile AI testing"""
    try:
        update_test_status(session_id, 'running', 10, 'Loading configuration...')
        test_config = load_config_yaml()
        
        # Initialize components
        update_test_status(session_id, progress=20, message='Initializing components...')
        emulator = EmulatorManager(test_config)
        apk_installer = APKInstaller(test_config)
        ui_explorer = UIExplorer(test_config)
        report_generator = ReportGenerator(test_config)
        
        update_test_status(session_id, progress=30, message='Initializing AI agent...')
        
        if AI_AVAILABLE:
            gemini_api_key = config.GEMINI_API_KEY
            if not gemini_api_key:
                 gemini_api_key = 'AIzaSyDeET9gqOoeQ1Kb84LZEC5dhsm6Tm7fUN4'
            
            ai_agent = AITestingAgent(test_config, gemini_api_key)
            
            if test_mode == 'guided' and test_context:
                ai_agent.app_context['user_context'] = test_context
            if test_mode == 'custom' and ai_instructions:
                ai_agent.app_context['custom_instructions'] = ai_instructions
            if credentials.get('hasLogin') and credentials.get('username'):
                ai_agent.app_context['credentials'] = credentials
            
            def log_callback(message):
                update_test_status(session_id, message=message)
            
            test_executor = AITestExecutor(test_config, ui_explorer, apk_installer, ai_agent, status_callback=log_callback)
        else:
            from ..agents.mobile.test_executor import TestExecutor
            test_executor = TestExecutor(test_config, ui_explorer, apk_installer)
        
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
        
        duration = time.time() - (active_tests[session_id].get('created_at') or time.time())
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

def run_web_test_logic(session_id, url):
    """Run Web testing using Playwright"""
    try:
        update_test_status(session_id, 'running', 10, f'Connecting to {url}...')
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
