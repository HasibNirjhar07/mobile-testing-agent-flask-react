"""
APK Installer - Handles APK installation and app management
"""
import subprocess
import time
import re
from loguru import logger

class APKInstaller:
    def __init__(self, config):
        self.config = config
        self.device_id = config['adb']['device_id']
        self.package_name = None
        self.main_activity = None
    
    def install(self, apk_path):
        """Install APK on device"""
        logger.info(f"Installing APK: {apk_path}")
        
        try:
            # Get package info before installation
            self.package_name = self._get_package_name(apk_path)
            self.main_activity = self._get_main_activity(apk_path)
            
            logger.info(f"Package: {self.package_name}")
            logger.info(f"Main Activity: {self.main_activity}")
            
            # Uninstall if already exists
            self.uninstall()
            
            # Install APK
            result = subprocess.run(
                ["adb", "-s", self.device_id, "install", "-r", apk_path],
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                text=True,
                timeout=120
            )
            
            if "Success" in result.stdout:
                logger.info("APK installed successfully")
                time.sleep(2)
                
                # Grant permissions immediately
                self.grant_permissions()
                
                # Perform warm-up launches to prevent first-run crashes
                logger.info("Performing warm-up launches to stabilize app...")
                self._warmup_app()
                
                return True
            else:
                logger.error(f"Installation failed: {result.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install APK: {str(e)}")
            return False
    
    def _warmup_app(self):
        """Launch app multiple times to warm up and prevent first-run issues"""
        for i in range(2):
            logger.info(f"Warm-up launch {i + 1}/2...")
            try:
                component = f"{self.package_name}/{self.main_activity}"
                subprocess.run(
                    ["adb", "-s", self.device_id, "shell", "am", "start", "-n", component],
                    capture_output=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=30
                )
                time.sleep(5)
                
                # Stop the app
                subprocess.run(
                    ["adb", "-s", self.device_id, "shell", "am", "force-stop", self.package_name],
                    capture_output=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=10
                )
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Warm-up {i + 1} failed: {str(e)}")
        
        logger.info("App warm-up complete")
    
    def uninstall(self):
        """Uninstall app from device"""
        if not self.package_name:
            return
        
        logger.info(f"Uninstalling: {self.package_name}")
        
        try:
            subprocess.run(
                ["adb", "-s", self.device_id, "uninstall", self.package_name],
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30
            )
        except Exception as e:
            logger.warning(f"Uninstall warning: {str(e)}")
    
    def launch(self):
        """Launch the installed app with retry mechanism"""
        if not self.package_name or not self.main_activity:
            logger.error("Package name or main activity not set")
            return False
        
        logger.info(f"Launching app: {self.package_name}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Stop app first to ensure clean state
                self.stop()
                time.sleep(2)
                
                # Clear app data on first attempt to prevent state issues
                if attempt == 0:
                    logger.info("Clearing app data for clean start...")
                    subprocess.run(
                        ["adb", "-s", self.device_id, "shell", "pm", "clear", self.package_name],
                        capture_output=True,
                        encoding="utf-8",
                        errors="ignore",
                        timeout=10
                    )
                    time.sleep(1)
                
                component = f"{self.package_name}/{self.main_activity}"
                result = subprocess.run(
                    ["adb", "-s", self.device_id, "shell", "am", "start", "-n", component],
                    capture_output=True,
                    encoding="utf-8",
                    errors="ignore",
                    text=True,
                    timeout=30
                )
                
                # Wait for app to launch
                time.sleep(5)
                
                # Verify app is running
                if self._is_app_running():
                    logger.info(f"App launched successfully (attempt {attempt + 1})")
                    return True
                else:
                    logger.warning(f"App may have crashed (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        logger.info("Retrying app launch...")
                        time.sleep(3)
                    
            except Exception as e:
                logger.error(f"Failed to launch app (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(3)
        
        logger.error("Failed to launch app after all retries")
        return False
    
    def _is_app_running(self):
        """Check if app is currently running"""
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "pidof", self.package_name],
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                text=True,
                timeout=5
            )
            
            # If pidof returns a number, app is running
            if result.stdout.strip() and result.stdout.strip().isdigit():
                return True
            
            # Fallback: check running processes
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "ps | grep", self.package_name],
                capture_output=True,
                text=True,
                timeout=5,
                encoding="utf-8",
                errors="ignore",
                shell=True
            )
            
            return self.package_name in result.stdout
            
        except Exception:
            return False
    
    def stop(self):
        """Stop the running app"""
        if not self.package_name:
            return
        
        logger.info(f"Stopping app: {self.package_name}")
        
        try:
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "am", "force-stop", self.package_name],
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Stop warning: {str(e)}")
    
    def _get_package_name(self, apk_path):
        """Extract package name from APK"""
        try:
            result = subprocess.run(
                ["aapt", "dump", "badging", apk_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30
            )
            
            match = re.search(r"package: name='([^']+)'", result.stdout)
            if match:
                return match.group(1)
            
            logger.error("Could not extract package name")
            return None
            
        except FileNotFoundError:
            logger.error("aapt not found. Make sure Android SDK build-tools is in PATH")
            # Fallback method using apkanalyzer
            return self._get_package_name_fallback(apk_path)
        except Exception as e:
            logger.error(f"Failed to get package name: {str(e)}")
            return None
    
    def _get_package_name_fallback(self, apk_path):
        """Fallback method using apkanalyzer"""
        try:
            result = subprocess.run(
                ["apkanalyzer", "manifest", "application-id", apk_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30
            )
            return result.stdout.strip()
        except Exception:
            return None
    
    def _get_main_activity(self, apk_path):
        """Extract main activity from APK"""
        try:
            result = subprocess.run(
                ["aapt", "dump", "badging", apk_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30
            )
            
            match = re.search(r"launchable-activity: name='([^']+)'", result.stdout)
            if match:
                return match.group(1)
            
            logger.error("Could not extract main activity")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get main activity: {str(e)}")
            return None
    
    def grant_permissions(self):
        """Grant all runtime permissions to the app"""
        if not self.package_name:
            return
        
        logger.info("Granting permissions...")
        
        permissions = [
            "android.permission.CAMERA",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.RECORD_AUDIO"
        ]
        
        for permission in permissions:
            try:
                subprocess.run(
                    ["adb", "-s", self.device_id, "shell", "pm", "grant", 
                     self.package_name, permission],
                    capture_output=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=5
                )
            except Exception:
                pass  # Permission might not be needed