"""
Emulator Manager - Handles Android emulator lifecycle
"""
import subprocess
import time
import os
from loguru import logger

class EmulatorManager:
    def __init__(self, config):
        self.config = config
        self.emulator_name = config['emulator']['name']
        self.port = config['emulator']['port']
        self.wait_timeout = config['emulator']['wait_timeout']
        self.process = None
        
    def start(self):
        """Start the Android emulator"""
        logger.info(f"Starting emulator: {self.emulator_name}")
        
        try:
            # Check if emulator already running
            if self.is_running():
                logger.info("Emulator already running")
                return True
            
            # Start emulator in background
            emulator_path = self._get_emulator_path()
            cmd = [
                emulator_path,
                "-avd", self.emulator_name,
                "-port", str(self.port),
                "-no-snapshot-load",
                "-no-audio",
                "-gpu", "swiftshader_indirect"
            ]
            
            logger.debug(f"Command: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for emulator to boot
            logger.info("Waiting for emulator to boot...")
            if self._wait_for_boot():
                logger.info("Emulator started successfully")
                return True
            else:
                logger.error("Emulator failed to boot within timeout")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start emulator: {str(e)}")
            return False
    
    def stop(self):
        """Stop the Android emulator"""
        logger.info("Stopping emulator...")
        
        try:
            # Kill using ADB
            device_id = f"emulator-{self.port}"
            subprocess.run(
                ["adb", "-s", device_id, "emu", "kill"],
                timeout=10
            )
            
            # Kill process if still running
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
            
            logger.info("Emulator stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop emulator: {str(e)}")
            return False
    
    def is_running(self):
        """Check if emulator is running"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            device_id = f"emulator-{self.port}"
            return device_id in result.stdout
            
        except Exception as e:
            logger.error(f"Failed to check emulator status: {str(e)}")
            return False
    
    def _wait_for_boot(self):
        """Wait for emulator to fully boot"""
        device_id = f"emulator-{self.port}"
        start_time = time.time()
        
        while time.time() - start_time < self.wait_timeout:
            try:
                # Check if device is online
                result = subprocess.run(
                    ["adb", "-s", device_id, "shell", "getprop", "sys.boot_completed"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if "1" in result.stdout.strip():
                    # Wait additional time for system to stabilize
                    time.sleep(10)
                    return True
                    
            except Exception:
                pass
            
            time.sleep(2)
        
        return False
    
    def _get_emulator_path(self):
        """Get path to emulator executable"""
        android_home = os.environ.get('ANDROID_HOME')
        
        if not android_home:
            raise Exception("ANDROID_HOME environment variable not set")
        
        if os.name == 'nt':  # Windows
            emulator_path = os.path.join(android_home, 'emulator', 'emulator.exe')
        else:  # Linux/macOS
            emulator_path = os.path.join(android_home, 'emulator', 'emulator')
        
        if not os.path.exists(emulator_path):
            raise Exception(f"Emulator not found at: {emulator_path}")
        
        return emulator_path
    
    def restart(self):
        """Restart the emulator"""
        logger.info("Restarting emulator...")
        self.stop()
        time.sleep(5)
        return self.start()