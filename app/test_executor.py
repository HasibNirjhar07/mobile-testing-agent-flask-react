"""
Test Executor - Main testing logic with exploration strategies
"""
import time
import random
from collections import deque
from loguru import logger

class TestExecutor:
    def __init__(self, config, ui_explorer, apk_installer):
        self.config = config
        self.ui = ui_explorer
        self.apk = apk_installer
        self.test_results = []
        self.exploration_queue = deque()
        self.action_history = []
        self.max_depth = config['testing']['max_exploration_depth']
        self.max_clicks = config['testing']['max_clicks_per_screen']
    
    def run_tests(self, documentation=None):
        """Run all tests"""
        logger.info("Starting automated testing...")
        
        start_time = time.time()
        
        # Phase 1: Initial exploration
        logger.info("Phase 1: Exploring app structure...")
        self._explore_app()
        
        # Phase 2: Test common flows
        logger.info("Phase 2: Testing common flows...")
        self._test_common_flows()
        
        # Phase 3: Test forms if found
        logger.info("Phase 3: Testing form inputs...")
        self._test_forms()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Testing completed in {duration:.2f} seconds")
        logger.info(f"Total screens explored: {len(self.ui.visited_screens)}")
        logger.info(f"Total actions performed: {len(self.action_history)}")
        
        return self._generate_results_summary()
    
    def _explore_app(self):
        """Explore app using hybrid strategy"""
        strategy = self.config['exploration']['strategy']
        
        # Reset and launch app
        self.apk.stop()
        self.apk.launch()
        time.sleep(3)
        
        # Take initial screenshot
        screenshot = self.ui.take_screenshot("initial_screen")
        self._record_action("Launch App", True, screenshot)
        
        visited_depth = 0
        clicks_on_screen = 0
        stuck_count = 0
        
        while visited_depth < self.max_depth:
            # Get current screen elements
            elements = self.ui.extract_elements()
            
            if not elements:
                logger.warning("No interactive elements found")
                break
            
            # Filter already clicked elements on this screen
            new_elements = [e for e in elements if self._is_new_element(e)]
            
            if not new_elements or clicks_on_screen >= self.max_clicks:
                # Try scrolling to reveal more elements
                if clicks_on_screen < self.max_clicks:
                    self.ui.scroll_down()
                    elements = self.ui.extract_elements()
                    new_elements = [e for e in elements if self._is_new_element(e)]
                
                # If still no new elements, go back
                if not new_elements:
                    logger.info("No more elements to explore, going back...")
                    self.ui.press_back()
                    time.sleep(1)
                    
                    # Check if we're stuck
                    current_hash = self.ui.get_screen_hash()
                    if current_hash in self.ui.visited_screens:
                        stuck_count += 1
                        if stuck_count > 3:
                            logger.warning("Stuck in loop, restarting app...")
                            self.apk.stop()
                            self.apk.launch()
                            time.sleep(3)
                            stuck_count = 0
                            visited_depth = 0
                    
                    clicks_on_screen = 0
                    continue
            
            # Select element based on strategy
            if strategy == "random":
                element = random.choice(new_elements)
            elif strategy == "bfs":
                element = new_elements[0]  # First element
            elif strategy == "dfs":
                element = new_elements[-1]  # Last element
            else:  # hybrid
                element = self._smart_select_element(new_elements)
            
            # Perform action
            element_desc = element['text'] or element['content_desc'] or element['type']
            logger.info(f"Clicking: {element_desc}")
            
            # Take screenshot before action
            screenshot_before = self.ui.take_screenshot(f"before_{element_desc[:20]}")
            
            # Click element
            success = self.ui.tap_element(element)
            time.sleep(2)
            
            # Take screenshot after action
            screenshot_after = self.ui.take_screenshot(f"after_{element_desc[:20]}")
            
            # Record action
            self._record_action(
                f"Click {element_desc}",
                success,
                screenshot_after,
                element
            )
            
            # Check if new screen
            if self.ui.is_new_screen():
                logger.info("New screen discovered!")
                visited_depth += 1
                clicks_on_screen = 0
                stuck_count = 0
            else:
                clicks_on_screen += 1
            
            # Small delay between actions
            time.sleep(1)
    
    def _test_common_flows(self):
        """Test common app flows"""
        # Restart app
        self.apk.stop()
        self.apk.launch()
        time.sleep(3)
        
        # Test navigation patterns
        self._test_navigation()
        
        # Test back button behavior
        self._test_back_button()
    
    def _test_navigation(self):
        """Test navigation through app"""
        logger.info("Testing navigation...")
        
        for i in range(5):  # Test 5 random navigation paths
            elements = self.ui.extract_elements()
            
            if not elements:
                break
            
            # Find navigation elements (tabs, menu items, etc.)
            nav_elements = [e for e in elements if 
                          'tab' in e['type'].lower() or
                          'menu' in e['type'].lower() or
                          'navigation' in e['resource_id'].lower()]
            
            if nav_elements:
                element = random.choice(nav_elements)
                screenshot = self.ui.take_screenshot(f"nav_test_{i}")
                self.ui.tap_element(element)
                time.sleep(2)
                
                self._record_action(
                    f"Navigation Test {i+1}",
                    True,
                    screenshot,
                    element
                )
    
    def _test_back_button(self):
        """Test back button functionality"""
        logger.info("Testing back button...")
        
        # Perform several actions
        for i in range(3):
            elements = self.ui.extract_elements()
            if elements:
                element = random.choice(elements)
                self.ui.tap_element(element)
                time.sleep(1)
        
        # Press back multiple times
        for i in range(3):
            screenshot = self.ui.take_screenshot(f"back_test_{i}")
            self.ui.press_back()
            time.sleep(1)
            
            self._record_action(
                f"Back Button Test {i+1}",
                True,
                screenshot
            )
    
    def _test_forms(self):
        """Test form inputs"""
        logger.info("Testing forms...")
        
        # Restart app
        self.apk.stop()
        self.apk.launch()
        time.sleep(3)
        
        # Look for input fields
        elements = self.ui.extract_elements()
        input_fields = [e for e in elements if 
                       'EditText' in e['type'] or
                       'edit' in e['resource_id'].lower() or
                       'input' in e['resource_id'].lower()]
        
        test_data = {
            'email': 'test@example.com',
            'username': 'testuser123',
            'password': 'Test@1234',
            'name': 'John Doe',
            'phone': '1234567890',
            'default': 'Test Input'
        }
        
        for field in input_fields:
            # Determine field type from hints
            field_id = field['resource_id'].lower()
            field_text = field['text'].lower()
            
            test_value = test_data['default']
            if 'email' in field_id or 'email' in field_text:
                test_value = test_data['email']
            elif 'user' in field_id or 'user' in field_text:
                test_value = test_data['username']
            elif 'pass' in field_id or 'pass' in field_text:
                test_value = test_data['password']
            elif 'name' in field_id or 'name' in field_text:
                test_value = test_data['name']
            elif 'phone' in field_id or 'phone' in field_text:
                test_value = test_data['phone']
            
            screenshot = self.ui.take_screenshot(f"form_input_{field_id[:20]}")
            success = self.ui.input_text(field, test_value)
            
            self._record_action(
                f"Input text in {field_id}",
                success,
                screenshot,
                field
            )
            
            time.sleep(1)
    
    def _smart_select_element(self, elements):
        """Smart element selection based on priority"""
        # Priority order:
        # 1. Buttons with important text (login, submit, etc.)
        # 2. Navigation elements
        # 3. Other clickable elements
        
        important_keywords = ['login', 'sign', 'submit', 'next', 'continue', 'ok', 'yes']
        
        # Find high priority elements
        high_priority = []
        for elem in elements:
            text = (elem['text'] + elem['content_desc']).lower()
            if any(keyword in text for keyword in important_keywords):
                high_priority.append(elem)
        
        if high_priority:
            return random.choice(high_priority)
        
        # Find navigation elements
        nav_elements = [e for e in elements if 
                       'tab' in e['type'].lower() or
                       'menu' in e['type'].lower()]
        
        if nav_elements:
            return random.choice(nav_elements)
        
        # Return random element
        return random.choice(elements)
    
    def _is_new_element(self, element):
        """Check if element hasn't been clicked yet"""
        element_signature = f"{element['resource_id']}_{element['text']}_{element['bounds']}"
        
        for action in self.action_history:
            if action.get('element'):
                prev_signature = f"{action['element'].get('resource_id', '')}_{action['element'].get('text', '')}_{action['element'].get('bounds', '')}"
                if element_signature == prev_signature:
                    return False
        
        return True
    
    def _record_action(self, action_name, success, screenshot=None, element=None):
        """Record an action in history"""
        action_record = {
            'action': action_name,
            'success': success,
            'screenshot': screenshot,
            'element': element,
            'timestamp': time.time()
        }
        
        self.action_history.append(action_record)
        
        # Also add to test results
        self.test_results.append({
            'test_name': action_name,
            'status': 'PASS' if success else 'FAIL',
            'screenshot': screenshot,
            'details': self._element_details(element) if element else None
        })
    
    def _element_details(self, element):
        """Get readable element details"""
        if not element:
            return None
        
        return {
            'type': element['type'],
            'text': element['text'],
            'resource_id': element['resource_id'],
            'content_desc': element['content_desc']
        }
    
    def _generate_results_summary(self):
        """Generate summary of test results"""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = total_tests - passed
        
        summary = {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'screens_explored': len(self.ui.visited_screens),
            'test_results': self.test_results,
            'action_history': self.action_history
        }
        
        return summary