"""
UI Explorer - Explores app UI and extracts element hierarchy
"""
import subprocess
import xml.etree.ElementTree as ET
import time
import hashlib
from pathlib import Path
from loguru import logger

class UIExplorer:
    def __init__(self, config):
        self.config = config
        self.device_id = config['adb']['device_id']
        self.screenshot_dir = Path(config['report']['screenshot_dir'])
        self.screenshot_dir.mkdir(exist_ok=True)
        self.visited_screens = set()
        self.screen_graph = {}
        self.current_screen_hash = None
    
    def get_ui_hierarchy(self):
        """Get current screen's UI hierarchy"""
        try:
            # Dump UI hierarchy
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "uiautomator", "dump", 
                 "/sdcard/window_dump.xml"],
                capture_output=True,
                timeout=10
            )
            
            # Pull the file
            subprocess.run(
                ["adb", "-s", self.device_id, "pull", "/sdcard/window_dump.xml", 
                 "temp_hierarchy.xml"],
                capture_output=True,
                timeout=10
            )
            
            # Parse XML
            tree = ET.parse("temp_hierarchy.xml")
            root = tree.getroot()
            
            return root
            
        except Exception as e:
            logger.error(f"Failed to get UI hierarchy: {str(e)}")
            return None
    
    def extract_elements(self, root=None):
        """Extract interactive elements from UI hierarchy"""
        if root is None:
            root = self.get_ui_hierarchy()
        
        if root is None:
            return []
        
        elements = []
        
        def traverse(node):
            # Check if element is clickable or has text
            clickable = node.get('clickable', 'false') == 'true'
            checkable = node.get('checkable', 'false') == 'true'
            long_clickable = node.get('long-clickable', 'false') == 'true'
            scrollable = node.get('scrollable', 'false') == 'true'
            text = node.get('text', '')
            content_desc = node.get('content-desc', '')
            resource_id = node.get('resource-id', '')
            class_name = node.get('class', '')
            bounds = node.get('bounds', '')
            
            # Parse bounds [x1,y1][x2,y2]
            center = self._parse_bounds(bounds)
            
            if (clickable or checkable or long_clickable or scrollable) and center:
                element = {
                    'type': class_name.split('.')[-1],
                    'text': text,
                    'content_desc': content_desc,
                    'resource_id': resource_id,
                    'clickable': clickable,
                    'checkable': checkable,
                    'long_clickable': long_clickable,
                    'scrollable': scrollable,
                    'bounds': bounds,
                    'center': center,
                    'class': class_name
                }
                elements.append(element)
            
            # Traverse children
            for child in node:
                traverse(child)
        
        traverse(root)
        return elements
    
    def _parse_bounds(self, bounds_str):
        """Parse bounds string to get center coordinates"""
        try:
            # Format: [x1,y1][x2,y2]
            import re
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
            if len(matches) == 2:
                x1, y1 = int(matches[0][0]), int(matches[0][1])
                x2, y2 = int(matches[1][0]), int(matches[1][1])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                return (center_x, center_y)
        except Exception:
            pass
        return None
    
    def take_screenshot(self, name="screen"):
        """Take screenshot of current screen"""
        try:
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            # Take screenshot
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "screencap", 
                 "/sdcard/screenshot.png"],
                capture_output=True,
                timeout=10
            )
            
            # Pull screenshot
            subprocess.run(
                ["adb", "-s", self.device_id, "pull", "/sdcard/screenshot.png", 
                 str(filepath)],
                capture_output=True,
                timeout=10
            )
            
            logger.info(f"Screenshot saved: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def get_screen_hash(self):
        """Get hash of current screen for duplicate detection"""
        try:
            root = self.get_ui_hierarchy()
            if root is None:
                return None
            
            # Create hash from element structure
            elements = self.extract_elements(root)
            screen_signature = ""
            
            for elem in elements:
                screen_signature += f"{elem['type']}_{elem['resource_id']}_{elem['text']}_"
            
            screen_hash = hashlib.md5(screen_signature.encode()).hexdigest()
            return screen_hash
            
        except Exception as e:
            logger.error(f"Failed to get screen hash: {str(e)}")
            return None
    
    def is_new_screen(self):
        """Check if current screen is new"""
        screen_hash = self.get_screen_hash()
        if screen_hash and screen_hash not in self.visited_screens:
            self.visited_screens.add(screen_hash)
            self.current_screen_hash = screen_hash
            return True
        self.current_screen_hash = screen_hash
        return False
    
    def tap_element(self, element):
        """Tap on an element"""
        try:
            x, y = element['center']
            logger.debug(f"Tapping at ({x}, {y}): {element['text'] or element['content_desc']}")
            
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)],
                capture_output=True,
                timeout=5
            )
            
            time.sleep(self.config['testing']['screenshot_delay'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to tap element: {str(e)}")
            return False
    
    def input_text(self, element, text):
        """Input text into an element"""
        try:
            # Tap to focus
            self.tap_element(element)
            time.sleep(0.5)
            
            # Clear existing text
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "keyevent", "KEYCODE_MOVE_END"],
                capture_output=True,
                timeout=5
            )
            
            for _ in range(50):  # Clear up to 50 characters
                subprocess.run(
                    ["adb", "-s", self.device_id, "shell", "input", "keyevent", "KEYCODE_DEL"],
                    capture_output=True,
                    timeout=5
                )
            
            # Input new text
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "text", text.replace(" ", "%s")],
                capture_output=True,
                timeout=5
            )
            
            logger.debug(f"Input text: {text}")
            time.sleep(0.5)
            return True
            
        except Exception as e:
            logger.error(f"Failed to input text: {str(e)}")
            return False
    
    def press_back(self):
        """Press back button"""
        try:
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "keyevent", "KEYCODE_BACK"],
                capture_output=True,
                timeout=5
            )
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Failed to press back: {str(e)}")
            return False
    
    def scroll_down(self):
        """Vertical scroll down"""
        try:
            # Get screen dimensions dynamically
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "wm", "size"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse: Physical size: 1080x2340
            if result.stdout and ':' in result.stdout:
                size = result.stdout.split(':')[1].strip()
                width, height = map(int, size.split('x'))
            else:
                # Fallback to default resolution
                width, height = 1080, 2340
            
            # Swipe from bottom to top (vertical scroll)
            x = int(width * 0.5)
            start_y = int(height * 0.7)
            end_y = int(height * 0.3)
            
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "swipe",
                 str(x), str(start_y), str(x), str(end_y), "300"],
                capture_output=True,
                timeout=5
            )
            
            logger.info(f"📜 Scrolled down ({x},{start_y}) -> ({x},{end_y})")
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Scroll down failed: {str(e)}")
            return False
    
    def swipe_left(self):
        """Swipe left (for ViewPagers, carousels)"""
        try:
            # Get screen dimensions dynamically
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "wm", "size"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse: Physical size: 1080x2340
            if result.stdout and ':' in result.stdout:
                size = result.stdout.split(':')[1].strip()
                width, height = map(int, size.split('x'))
            else:
                # Fallback to default resolution
                width, height = 1080, 2340
            
            # Swipe from right to left (80% to 20% of width, middle height)
            start_x = int(width * 0.8)
            end_x = int(width * 0.2)
            y = int(height * 0.5)
            
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "swipe",
                 str(start_x), str(y), str(end_x), str(y), "300"],
                capture_output=True,
                timeout=5
            )
            
            logger.info(f"👉 Swiped left ({start_x},{y}) -> ({end_x},{y})")
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Swipe left failed: {str(e)}")
            return False

    def swipe_right(self):
        """Swipe right (for ViewPagers, carousels)"""
        try:
            # Get screen dimensions dynamically
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "wm", "size"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse: Physical size: 1080x2340
            if result.stdout and ':' in result.stdout:
                size = result.stdout.split(':')[1].strip()
                width, height = map(int, size.split('x'))
            else:
                # Fallback to default resolution
                width, height = 1080, 2340
            
            # Swipe from left to right
            start_x = int(width * 0.2)
            end_x = int(width * 0.8)
            y = int(height * 0.5)
            
            subprocess.run(
                ["adb", "-s", self.device_id, "shell", "input", "swipe",
                 str(start_x), str(y), str(end_x), str(y), "300"],
                capture_output=True,
                timeout=5
            )
            
            logger.info(f"👈 Swiped right ({start_x},{y}) -> ({end_x},{y})")
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Swipe right failed: {str(e)}")
            return False