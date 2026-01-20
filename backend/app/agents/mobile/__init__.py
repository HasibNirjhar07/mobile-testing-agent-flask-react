"""
AI-Powered Automated Mobile App Testing Agent
"""

__version__ = "2.0.0"
__author__ = "Hasib Nirjhar"

from .emulator_manager import EmulatorManager
from .apk_installer import APKInstaller
from .ui_explorer import UIExplorer
from .test_executor import TestExecutor
from .report_generator import ReportGenerator
from .ai_agent_core import AITestingAgent
from .ai_test_executor import AITestExecutor

__all__ = [
    'EmulatorManager',
    'APKInstaller',
    'UIExplorer',
    'TestExecutor',
    'ReportGenerator',
    'AITestingAgent',
    'AITestExecutor'
]