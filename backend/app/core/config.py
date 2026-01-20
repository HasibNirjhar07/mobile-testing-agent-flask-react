import os
from pathlib import Path
from dotenv import load_dotenv

# Load env from backend/.env
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    REPORT_FOLDER = BASE_DIR / 'reports'
    SCREENSHOT_FOLDER = BASE_DIR / 'screenshots'
    
    # Ensure directories exist
    @classmethod
    def ensure_dirs(cls):
        cls.UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
        cls.REPORT_FOLDER.mkdir(exist_ok=True, parents=True)
        cls.SCREENSHOT_FOLDER.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def setup_android_env():
        # Common Default Paths for Windows
        if not os.environ.get('ANDROID_HOME'):
            possible_paths = [
                r'C:\Users\hasib\AppData\Local\Android\Sdk',
                os.path.expanduser('~\\AppData\\Local\\Android\\Sdk'),
                r'C:\Program Files\Android\Android Studio\plugins\android\lib\sdk'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    os.environ['ANDROID_HOME'] = path
                    # Add to PATH
                    platform_tools = os.path.join(path, 'platform-tools')
                    emulator = os.path.join(path, 'emulator')
                    if os.path.exists(platform_tools):
                         os.environ['PATH'] += os.pathsep + platform_tools
                    if os.path.exists(emulator):
                         os.environ['PATH'] += os.pathsep + emulator
                    break

Config.ensure_dirs()
Config.setup_android_env()

# Export instance/class aliased as config
config = Config
