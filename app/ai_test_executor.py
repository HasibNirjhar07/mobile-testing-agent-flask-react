"""
AI-Powered Test Executor - Intelligent test execution with Gemini
"""
import time
import random
from collections import deque
from loguru import logger
from .ai_agent_core import AITestingAgent

class AITestExecutor:
    def __init__(self, config, ui_explorer, apk_installer, ai_agent: AITestingAgent):
        self.config = config
        self.ui = ui_explorer
        self.apk = apk_installer
        self.ai = ai_agent
        self.test_results = []
        self.action_history = []
        self.max_depth = config['testing']['max_exploration_depth']
        self.stuck_threshold = 3
        self.stuck_count = 0
    
    def run_tests(self, documentation=None):
        """Run AI-powered automated testing"""
        logger.info("🤖 Starting AI-powered automated testing...")
        
        start_time = time.time()
        
        # Phase 1: AI analyzes app structure
        logger.info("\n" + "="*60)
        logger.info("Phase 1: AI App Analysis")
        logger.info("="*60)
        
        test_strategy = self._ai_analyze_app()
        
        # Phase 2: AI-guided exploration
        logger.info("\n" + "="*60)
        logger.info("Phase 2: AI-Guided Exploration")
        logger.info("="*60)
        
        self._ai_guided_exploration(test_strategy)
        
        # Phase 3: AI-powered form testing
        logger.info("\n" + "="*60)
        logger.info("Phase 3: Intelligent Form Testing")
        logger.info("="*60)
        
        self._ai_test_forms()
        
        # Phase 4: Critical scenario testing
        logger.info("\n" + "="*60)
        logger.info("Phase 4: Critical Scenario Testing")
        logger.info("="*60)
        
        self._test_critical_scenarios(test_strategy.get('critical_scenarios', []))
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"\n✅ Testing completed in {duration:.2f} seconds")
        logger.info(f"📊 Total screens explored: {len(self.ui.visited_screens)}")
        logger.info(f"🎯 Total actions performed: {len(self.action_history)}")
        
        return self._generate_results_summary()
    
    def _ai_analyze_app(self):
        """Initial AI analysis of the app"""
        # Launch app
        self.apk.stop()
        time.sleep(2)
        self.apk.launch()
        time.sleep(5)
        
        # Take initial screenshot
        initial_screenshot = self.ui.take_screenshot("ai_initial_analysis")
        
        if not initial_screenshot:
            logger.error("Failed to capture initial screenshot")
            return self.ai._get_default_strategy()
        
        # Get APK info
        apk_info = {
            'package_name': self.apk.package_name,
            'main_activity': self.apk.main_activity
        }
        
        # AI analyzes app
        strategy = self.ai.analyze_app_structure(apk_info, initial_screenshot)
        
        logger.info(f"📱 App Type: {strategy.get('app_type', 'Unknown')}")
        logger.info(f"🎯 Core Features: {', '.join(strategy.get('core_features', [])[:5])}")
        logger.info(f"⚡ Critical Scenarios: {len(strategy.get('critical_scenarios', []))}")
        
        return strategy
    
    def _ai_guided_exploration(self, strategy):
        """AI guides the exploration process"""
        exploration_count = 0
        max_explorations = self.max_depth * 3  # Allow more actions with AI
        
        while exploration_count < max_explorations:
            # Get current UI elements
            elements = self.ui.extract_elements()
            
            if not elements:
                logger.warning("No elements found, trying back button")
                self.ui.press_back()
                time.sleep(2)
                self.stuck_count += 1
                
                if self.stuck_count >= self.stuck_threshold:
                    logger.warning("Stuck detected, restarting app...")
                    self._restart_app()
                    self.stuck_count = 0
                    continue
                continue
            
            # Reset stuck counter when we find elements
            self.stuck_count = 0
            
            # Take screenshot before decision
            screenshot_before = self.ui.take_screenshot(f"before_action_{exploration_count}")
            
            # AI decides next action
            decision = self.ai.decide_next_action(
                screenshot_before,
                elements,
                self.action_history
            )
            
            if not decision:
                logger.warning("AI couldn't make decision, using fallback")
                decision = self._get_fallback_action(elements)
            
            # Execute decision
            success = self._execute_ai_decision(decision, elements, screenshot_before)
            
            if success:
                exploration_count += 1
                
                # Take screenshot after action
                screenshot_after = self.ui.take_screenshot(f"after_action_{exploration_count}")
                
                # AI analyzes transition
                if screenshot_before and screenshot_after:
                    analysis = self.ai.analyze_screen_transition(
                        screenshot_before,
                        screenshot_after,
                        decision.get('reasoning', 'Action performed')
                    )
                    
                    # Log analysis
                    if analysis.get('potential_issues'):
                        logger.warning(f"⚠️  Issues: {', '.join(analysis['potential_issues'])}")
                    
                    if not analysis.get('action_successful'):
                        logger.warning("⚠️  Action may have failed")
                
                # Check if we discovered new screen
                if self.ui.is_new_screen():
                    logger.info("🆕 New screen discovered!")
            else:
                logger.warning("Action execution failed")
            
            # Smart delay based on priority
            priority = decision.get('priority', 'medium')
            if priority == 'critical':
                time.sleep(3)  # More time for critical actions
            elif priority == 'high':
                time.sleep(2)
            else:
                time.sleep(1)
            
            # Progress update
            if exploration_count % 10 == 0:
                logger.info(f"Progress: {exploration_count}/{max_explorations} actions")
    

    def _execute_ai_decision(self, decision, elements, screenshot):
        """Execute AI's decision - with swipe support"""
        action_type = decision.get('action_type', 'tap')
        element_index = decision.get('element_index', -1)
        
        try:
            # System actions (no element needed)
            if action_type == 'back' or element_index < 0:
                if action_type == 'back':
                    logger.info("🔙 AI Decision: Go back")
                    self.ui.press_back()
                    self._record_action("AI: Press Back", True, screenshot, decision)
                    return True
                
                elif action_type == 'swipe_left':
                    logger.info("👉 AI Decision: Swipe left (next page)")
                    logger.info(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                    success = self.ui.swipe_left()
                    self._record_action("AI: Swipe Left", success, screenshot, decision)
                    return success
                
                elif action_type == 'swipe_right':
                    logger.info("👈 AI Decision: Swipe right (previous page)")
                    logger.info(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                    success = self.ui.swipe_right()
                    self._record_action("AI: Swipe Right", success, screenshot, decision)
                    return success
                
                elif action_type == 'scroll':
                    logger.info("📜 AI Decision: Scroll down")
                    logger.info(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                    success = self.ui.scroll_down()
                    self._record_action("AI: Scroll Down", success, screenshot, decision)
                    return success
                
                # Fallback to back if unknown
                self.ui.press_back()
                self._record_action("AI: Press Back (fallback)", True, screenshot, decision)
                return True
            
            # Element-based actions
            if element_index >= len(elements):
                logger.warning(f"Invalid element index: {element_index}")
                return False
            
            element = elements[element_index]
            
            if action_type == 'tap':
                element_desc = element['text'] or element['content_desc'] or element['type']
                logger.info(f"👆 AI Decision: Tap '{element_desc}'")
                logger.info(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                
                success = self.ui.tap_element(element)
                self._record_action(
                    f"AI: Tap {element_desc}",
                    success,
                    screenshot,
                    decision,
                    element
                )
                return success
            
            elif action_type == 'input':
                test_value = decision.get('test_value', 'Test Input')
                element_desc = element['text'] or element['resource_id'] or element['type']
                
                logger.info(f"⌨️  AI Decision: Input '{test_value}' into {element_desc}")
                logger.info(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                
                success = self.ui.input_text(element, test_value)
                self._record_action(
                    f"AI: Input into {element_desc}",
                    success,
                    screenshot,
                    decision,
                    element
                )
                return success
            
            elif action_type in ['swipe_left', 'swipe_right']:
                # Swipe on specific element (e.g., ViewPager)
                logger.info(f"↔️  AI Decision: {action_type} on {element['type']}")
                logger.info(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                
                if action_type == 'swipe_left':
                    success = self.ui.swipe_left()
                else:
                    success = self.ui.swipe_right()
                
                self._record_action(
                    f"AI: {action_type} on {element['type']}",
                    success,
                    screenshot,
                    decision,
                    element
                )
                return success
            
            elif action_type == 'scroll':
                logger.info(f"📜 AI Decision: Scroll on {element['type']}")
                success = self.ui.scroll_down()
                self._record_action(f"AI: Scroll on {element['type']}", success, screenshot, decision, element)
                return success
            
        except Exception as e:
            logger.error(f"Failed to execute AI decision: {str(e)}")
            return False
        
        return False
    def _ai_test_forms(self):
        """AI-powered form testing"""
        # Restart app to find forms
        self._restart_app()
        
        # Look for forms
        elements = self.ui.extract_elements()
        input_fields = [e for e in elements if 
                       'EditText' in e['type'] or
                       'edit' in e.get('resource_id', '').lower() or
                       'input' in e.get('resource_id', '').lower()]
        
        if not input_fields:
            logger.info("No input fields found, skipping form testing")
            return
        
        logger.info(f"Found {len(input_fields)} input fields")
        
        for field in input_fields[:5]:  # Test up to 5 fields
            # Identify field type
            field_id = field.get('resource_id', '').lower()
            field_text = field.get('text', '').lower()
            
            # AI suggests test values
            field_type = self._identify_field_type(field_id, field_text)
            test_values = self.ai.suggest_input_values(field_type, field_id)
            
            logger.info(f"Testing field: {field_id or field_text}")
            
            # Test each value
            for i, value in enumerate(test_values):
                if not value:
                    continue
                
                screenshot = self.ui.take_screenshot(f"form_test_{field_id}_{i}")
                
                # Tap field first
                self.ui.tap_element(field)
                time.sleep(1)
                
                # Input value
                success = self.ui.input_text(field, value)
                
                logger.info(f"  Test value {i+1}: '{value}' - {'✓' if success else '✗'}")
                
                self._record_action(
                    f"AI Form Test: {field_id} = {value}",
                    success,
                    screenshot,
                    {'reasoning': f'Testing {field_type} field with value: {value}'},
                    field
                )
                
                time.sleep(1)
    
    def _test_critical_scenarios(self, scenarios):
        """Test AI-identified critical scenarios"""
        if not scenarios:
            logger.info("No critical scenarios identified")
            return
        
        for scenario in scenarios[:3]:  # Test top 3 scenarios
            logger.info(f"🎯 Testing: {scenario.get('name', 'Unknown scenario')}")
            
            # Restart app for each scenario
            self._restart_app()
            
            steps = scenario.get('steps', [])
            for step in steps:
                logger.info(f"  Step: {step}")
                
                # Find elements matching step description
                elements = self.ui.extract_elements()
                
                # Simple matching - look for keywords in step
                matching_elements = []
                keywords = step.lower().split()
                
                for elem in elements:
                    elem_text = (elem.get('text', '') + ' ' + 
                                elem.get('content_desc', '') + ' ' + 
                                elem.get('resource_id', '')).lower()
                    
                    if any(keyword in elem_text for keyword in keywords):
                        matching_elements.append(elem)
                
                if matching_elements:
                    element = matching_elements[0]
                    screenshot = self.ui.take_screenshot(f"scenario_{scenario.get('name', 'test')}")
                    
                    self.ui.tap_element(element)
                    time.sleep(2)
                    
                    self._record_action(
                        f"Scenario: {step}",
                        True,
                        screenshot,
                        {'reasoning': f"Critical scenario: {scenario.get('name')}"},
                        element
                    )
                else:
                    logger.warning(f"  Could not find element for step: {step}")
    
    def _restart_app(self):
        """Restart app cleanly"""
        self.apk.stop()
        time.sleep(2)
        self.apk.launch()
        time.sleep(5)
    
    def _identify_field_type(self, field_id, field_text):
        """Identify field type from ID and text"""
        combined = (field_id + ' ' + field_text).lower()
        
        if 'email' in combined:
            return 'email'
        elif 'pass' in combined:
            return 'password'
        elif 'phone' in combined or 'mobile' in combined:
            return 'phone'
        elif 'name' in combined:
            return 'name'
        elif 'user' in combined:
            return 'username'
        
        return 'default'
    
    def _get_fallback_action(self, elements):
        """Fallback when AI fails"""
        import random
        if elements:
            return {
                'element_index': random.randint(0, len(elements) - 1),
                'action_type': 'tap',
                'reasoning': 'Fallback random action',
                'priority': 'low'
            }
        return {
            'element_index': -1,
            'action_type': 'back',
            'reasoning': 'No elements available'
        }
    
    def _record_action(self, action_name, success, screenshot=None, decision=None, element=None):
        """Record an action"""
        action_record = {
            'action': action_name,
            'success': success,
            'screenshot': screenshot,
            'element': element,
            'ai_decision': decision,
            'timestamp': time.time()
        }
        
        self.action_history.append(action_record)
        
        # Add to test results
        self.test_results.append({
            'test_name': action_name,
            'status': 'PASS' if success else 'FAIL',
            'screenshot': screenshot,
            'details': self._element_details(element) if element else None,
            'ai_reasoning': decision.get('reasoning') if decision else None
        })
    
    def _element_details(self, element):
        """Get element details"""
        if not element:
            return None
        
        return {
            'type': element.get('type', 'Unknown'),
            'text': element.get('text', ''),
            'resource_id': element.get('resource_id', ''),
            'content_desc': element.get('content_desc', '')
        }
    
    def _generate_results_summary(self):
        """Generate summary with AI insights"""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = total_tests - passed
        
        # Get AI insights
        ai_insights = self.ai.generate_test_report_insights(self.test_results)
        
        summary = {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'screens_explored': len(self.ui.visited_screens),
            'test_results': self.test_results,
            'action_history': self.action_history,
            'ai_insights': ai_insights,
            'app_context': self.ai.app_context
        }
        
        return summary