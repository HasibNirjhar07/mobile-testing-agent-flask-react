"""
AI Agent Core - Gemini-powered intelligent testing agent
"""
import google.generativeai as genai
import base64
import json
from pathlib import Path
from loguru import logger
from typing import List, Dict, Optional
import time

class AITestingAgent:
    def __init__(self, config, api_key: str):
        self.config = config
        genai.configure(api_key=api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Context management
        self.conversation_history = []
        self.app_context = {
            'package_name': None,
            'discovered_screens': [],
            'tested_flows': [],
            'identified_features': [],
            'potential_bugs': []
        }
        
        logger.info("AI Testing Agent initialized with Gemini")
    
    def analyze_app_structure(self, apk_info: Dict, initial_screenshot: str) -> Dict:
        """
        Analyze app structure and create test strategy
        """
        logger.info("🧠 AI analyzing app structure...")
        
        prompt = f"""You are an expert mobile app testing AI. Analyze this Android app and create a comprehensive test strategy.

App Information:
- Package: {apk_info.get('package_name', 'Unknown')}
- Main Activity: {apk_info.get('main_activity', 'Unknown')}

I will show you the initial screenshot. Based on this:

1. Identify the app type (e-commerce, social media, productivity, etc.)
2. List expected core features
3. Suggest critical test scenarios
4. Identify potential edge cases
5. Recommend exploration priority (which buttons/areas to test first)

Respond in JSON format:
{{
    "app_type": "type of app",
    "core_features": ["feature1", "feature2"],
    "critical_scenarios": [
        {{"name": "scenario", "steps": ["step1", "step2"], "priority": "high/medium/low"}}
    ],
    "edge_cases": ["case1", "case2"],
    "exploration_priority": ["element1", "element2"]
}}"""

        try:
            # Load and encode screenshot
            with open(initial_screenshot, 'rb') as img_file:
                img_data = img_file.read()
            
            response = self.model.generate_content([
                prompt,
                {
                    'mime_type': 'image/png',
                    'data': img_data
                }
            ])
            
            # Parse response
            result = self._parse_json_response(response.text)
            
            if result:
                self.app_context['app_type'] = result.get('app_type')
                self.app_context['identified_features'] = result.get('core_features', [])
                logger.info(f"✓ App identified as: {result.get('app_type')}")
                logger.info(f"✓ Found {len(result.get('core_features', []))} core features")
                return result
            
            return self._get_default_strategy()
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._get_default_strategy()
        
    """
    Enhanced AI decision logic with swipe detection and stuck detection
    Add/replace these methods in your AITestingAgent class
    """

    def decide_next_action(self, current_screenshot: str, 
                        available_elements: List[Dict],
                        action_history: List[Dict]) -> Dict:
        """
        AI decides the next best action - with swipe support and stuck detection
        """
        logger.info("🤖 AI deciding next action...")
        
        # Check if stuck (same action failing repeatedly)
        if self._is_stuck_in_loop(action_history):
            logger.warning("🔄 Detected stuck loop - trying alternative action")
            return self._get_unstuck_action(action_history, available_elements)
        
        # Prepare element descriptions
        elements_desc = []
        has_viewpager = False
        has_pagination_dots = False
        
        for i, elem in enumerate(available_elements[:15]):
            desc = f"{i}. {elem['type']}"
            if elem['text']:
                desc += f" - Text: '{elem['text']}'"
            if elem['content_desc']:
                desc += f" - Description: '{elem['content_desc']}'"
            if elem['resource_id']:
                desc += f" - ID: {elem['resource_id']}"
                # Detect ViewPager
                if 'viewpager' in elem['resource_id'].lower() or 'pager' in elem['resource_id'].lower():
                    has_viewpager = True
                # Detect pagination dots
                if 'dot' in elem['resource_id'].lower() or 'indicator' in elem['resource_id'].lower():
                    has_pagination_dots = True
            
            elements_desc.append(desc)
        
        # Get recent actions
        recent_actions = action_history[-5:] if len(action_history) > 5 else action_history
        actions_desc = [f"- {act['action']}" for act in recent_actions]
        
        # Enhanced context for ViewPager detection
        viewpager_hint = ""
        if has_viewpager or has_pagination_dots:
            viewpager_hint = """
            
    ⚠️ IMPORTANT: A ViewPager or pagination indicator was detected!
    - ViewPagers require HORIZONTAL SWIPES, not vertical scrolls
    - Use 'swipe_left' to go to the next page
    - Use 'swipe_right' to go to the previous page
    - DO NOT use 'scroll' for ViewPagers - it will not work!
    """
        
        prompt = f"""You are testing a mobile app. Based on the current screen and available elements, decide the BEST next action.

    App Context:
    - Type: {self.app_context.get('app_type', 'Unknown')}
    - Features to test: {', '.join(self.app_context.get('identified_features', [])[:5])}

    Recent Actions:
    {chr(10).join(actions_desc) if actions_desc else "No previous actions"}

    Available Elements:
    {chr(10).join(elements_desc)}
    {viewpager_hint}

    Choose the MOST IMPORTANT element to interact with. Prioritize:
    1. Login/Sign-up buttons (if not tested)
    2. Main navigation elements
    3. Feature-specific buttons
    4. Form fields
    5. Less critical UI elements

    Respond in JSON format:
    {{
        "element_index": 0,  // Index from the list above, or -1 for system actions
        "action_type": "tap|input|swipe_left|swipe_right|scroll|back",
        "reasoning": "Why this action is important",
        "expected_outcome": "What should happen",
        "test_value": "text to input (if action is input)",
        "priority": "critical|high|medium|low"
    }}

    CRITICAL RULES:
    - For ViewPagers with pagination dots: ALWAYS use "swipe_left" or "swipe_right", NEVER use "scroll"
    - For onboarding screens with multiple pages: use "swipe_left" to advance
    - For scrollable lists/content: use "scroll"
    - If previous action failed 3+ times, try a different action type
    - If no good actions available, set element_index to -1 and action_type to "back"."""

        try:
            # Include screenshot for context
            with open(current_screenshot, 'rb') as img_file:
                img_data = img_file.read()
            
            response = self.model.generate_content([
                prompt,
                {
                    'mime_type': 'image/png',
                    'data': img_data
                }
            ])
            
            decision = self._parse_json_response(response.text)
            
            if decision:
                # Validate action type
                valid_actions = ['tap', 'input', 'swipe_left', 'swipe_right', 'scroll', 'back']
                if decision.get('action_type') not in valid_actions:
                    logger.warning(f"Invalid action type: {decision.get('action_type')}, defaulting to tap")
                    decision['action_type'] = 'tap'
                
                logger.info(f"✓ AI Decision: {decision.get('reasoning', 'No reason')}")
                return decision
            
            return self._get_fallback_action(available_elements)
            
        except Exception as e:
            logger.error(f"AI decision failed: {str(e)}")
            return self._get_fallback_action(available_elements)

    def _is_stuck_in_loop(self, action_history: List[Dict], window: int = 5) -> bool:
        """
        Detect if the agent is stuck performing the same failing action repeatedly
        """
        if len(action_history) < window:
            return False
        
        # Get last N actions
        recent = action_history[-window:]
        
        # Check if all actions are the same type
        action_types = [act.get('ai_decision', {}).get('action_type') for act in recent if act.get('ai_decision')]
        
        if len(set(action_types)) == 1:  # All same action type
            # Check if any succeeded
            successes = [act.get('success', False) for act in recent]
            if not any(successes):
                logger.warning(f"🔄 Stuck detected: {action_types[0]} failed {window} times")
                return True
        
        return False

    def _get_unstuck_action(self, action_history: List[Dict], elements: List[Dict]) -> Dict:
        """
        Return an alternative action when stuck
        """
        # Get the action that's been failing
        last_action = action_history[-1].get('ai_decision', {}).get('action_type', '')
        
        logger.info(f"🔧 Attempting to get unstuck from: {last_action}")
        
        # Alternative action mapping
        alternatives = {
            'scroll': 'swipe_left',      # If scroll isn't working, try swipe
            'swipe_left': 'swipe_right',  # Try opposite direction
            'swipe_right': 'swipe_left',
            'tap': 'back',                # If tapping fails, go back
        }
        
        alternative = alternatives.get(last_action, 'back')
        
        return {
            'element_index': -1,
            'action_type': alternative,
            'reasoning': f'Unstuck action: {last_action} failed repeatedly, trying {alternative}',
            'priority': 'high',
            'expected_outcome': 'Break out of stuck state'
        }
        
    def analyze_screen_transition(self, before_screenshot: str, 
                                  after_screenshot: str,
                                  action_taken: str) -> Dict:
        """
        Analyze what happened after an action
        """
        logger.info("🔍 AI analyzing screen transition...")
        
        prompt = f"""Compare these two screenshots taken before and after the action: "{action_taken}"

Analyze:
1. Did the screen change?
2. Is this a new screen or a dialog/popup?
3. Are there any error messages?
4. Did the action succeed?
5. What new testing opportunities appeared?
6. Any potential bugs or issues?

Respond in JSON format:
{{
    "screen_changed": true/false,
    "transition_type": "new_screen|dialog|popup|no_change|error",
    "action_successful": true/false,
    "new_elements_of_interest": ["element1", "element2"],
    "potential_issues": ["issue1", "issue2"],
    "recommendations": ["next_action1", "next_action2"]
}}"""

        try:
            with open(before_screenshot, 'rb') as f1:
                before_data = f1.read()
            with open(after_screenshot, 'rb') as f2:
                after_data = f2.read()
            
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'image/png', 'data': before_data},
                "AFTER:",
                {'mime_type': 'image/png', 'data': after_data}
            ])
            
            analysis = self._parse_json_response(response.text)
            
            if analysis:
                if analysis.get('potential_issues'):
                    self.app_context['potential_bugs'].extend(analysis['potential_issues'])
                    logger.warning(f"⚠️  Potential issues detected: {analysis['potential_issues']}")
                
                return analysis
            
            return {'screen_changed': False, 'action_successful': True}
            
        except Exception as e:
            logger.error(f"Screen analysis failed: {str(e)}")
            return {'screen_changed': False, 'action_successful': True}
    
    def generate_test_report_insights(self, test_results: List[Dict]) -> str:
        """
        Generate AI-powered insights for test report
        """
        logger.info("📊 AI generating test insights...")
        
        # Prepare test summary
        total = len(test_results)
        passed = sum(1 for r in test_results if r['status'] == 'PASS')
        failed = total - passed
        
        actions = [r['test_name'] for r in test_results]
        
        prompt = f"""Analyze these mobile app test results and provide insights.

Test Summary:
- Total Tests: {total}
- Passed: {passed}
- Failed: {failed}

Actions Performed:
{chr(10).join(f"- {action}" for action in actions[:20])}

App Context:
- Type: {self.app_context.get('app_type', 'Unknown')}
- Discovered Features: {', '.join(self.app_context.get('identified_features', []))}

Potential Issues Found:
{chr(10).join(f"- {issue}" for issue in self.app_context.get('potential_bugs', []))}

Provide:
1. Overall app quality assessment
2. Test coverage analysis
3. Critical issues or concerns
4. Recommended additional tests
5. Security or UX observations

Write a comprehensive but concise report."""

        try:
            response = self.model.generate_content(prompt)
            insights = response.text
            
            logger.info("✓ AI insights generated")
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {str(e)}")
            return "AI insights unavailable."
    
    def suggest_input_values(self, field_type: str, field_id: str) -> List[str]:
        """
        AI suggests appropriate test values for input fields
        """
        prompt = f"""Suggest test input values for a mobile app form field.

Field Type: {field_type}
Field ID: {field_id}

Provide 3 test values:
1. Valid positive case
2. Boundary/edge case
3. Invalid/negative case (to test validation)

Respond in JSON format:
{{
    "positive": "valid value",
    "boundary": "edge case value",
    "negative": "invalid value"
}}"""
        
        ## before_action_0_1761995231

        try:
            response = self.model.generate_content(prompt)
            values = self._parse_json_response(response.text)
            
            if values:
                return [values.get('positive'), values.get('boundary'), values.get('negative')]
            
            return self._get_default_test_values(field_type)
            
        except Exception as e:
            logger.error(f"Input suggestion failed: {str(e)}")
            return self._get_default_test_values(field_type)
    
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """
        Parse JSON from AI response (handles markdown code blocks)
        """
        try:
            # Remove markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            # Clean up
            text = text.strip()
            
            return json.loads(text)
        except Exception as e:
            logger.warning(f"Failed to parse JSON: {str(e)}")
            return None
    
    def _get_default_strategy(self) -> Dict:
        """Fallback strategy when AI fails"""
        return {
            'app_type': 'Unknown',
            'core_features': ['Navigation', 'Basic UI'],
            'critical_scenarios': [],
            'edge_cases': [],
            'exploration_priority': []
        }
    
    def _get_fallback_action(self, elements: List[Dict]) -> Dict:
        """Fallback action when AI fails"""
        import random
        if elements:
            return {
                'element_index': 0,
                'action_type': 'tap',
                'reasoning': 'Fallback action',
                'priority': 'medium'
            }
        return {
            'element_index': -1,
            'action_type': 'back',
            'reasoning': 'No elements available'
        }
    
    def _get_default_test_values(self, field_type: str) -> List[str]:
        """Default test values by field type"""
        defaults = {
            'email': ['test@example.com', 'test+tag@example.com', 'invalid-email'],
            'password': ['Test@123456', 'a', '12345678'],
            'phone': ['1234567890', '123', 'abcdefghij'],
            'name': ['John Doe', 'A', 'X' * 100],
            'username': ['testuser123', 'ab', 'user@#$%'],
            'default': ['Test Input', '', 'X' * 200]
        }
        
        field_lower = field_type.lower()
        for key in defaults:
            if key in field_lower:
                return defaults[key]
        
        return defaults['default']