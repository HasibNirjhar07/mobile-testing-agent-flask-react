"""
Enhanced Report Generator - Creates beautiful HTML reports with AI insights
"""
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config['report']['output_dir'])
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, test_summary, apk_info):
        """Generate enhanced test report with AI insights"""
        logger.info("Generating enhanced test report...")
        
        report_format = self.config['report']['format']
        
        if report_format == 'html':
            return self._generate_html(test_summary, apk_info)
        elif report_format == 'json':
            return self._generate_json(test_summary, apk_info)
        else:
            logger.error(f"Unknown report format: {report_format}")
            return None
    
    def _generate_html(self, test_summary, apk_info):
        """Generate enhanced HTML report with AI insights"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_test_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        html_content = self._create_enhanced_html(test_summary, apk_info)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Enhanced HTML report generated: {filepath}")
        return str(filepath)
    
    def _create_enhanced_html(self, test_summary, apk_info):
        """Create enhanced HTML with AI insights"""
        total = test_summary['total_tests']
        passed = test_summary['passed']
        failed = test_summary['failed']
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Get AI-specific data
        ai_insights = test_summary.get('ai_insights', '')
        app_context = test_summary.get('app_context', {})
        app_type = app_context.get('app_type', 'Unknown')
        core_features = app_context.get('identified_features', [])
        potential_bugs = app_context.get('potential_bugs', [])
        
        # Format AI insights for HTML
        ai_insights_html = ai_insights.replace('\n', '<br>') if ai_insights else 'AI insights not available'
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI-Powered Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '🤖';
            position: absolute;
            font-size: 200px;
            opacity: 0.1;
            top: -30px;
            right: -30px;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }}
        
        .ai-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 25px;
            margin-top: 15px;
            font-size: 0.9em;
            backdrop-filter: blur(10px);
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            padding: 50px;
            background: linear-gradient(to bottom, #f8f9fa 0%, white 100%);
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            transition: all 0.3s;
            border: 2px solid transparent;
        }}
        
        .stat-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            border-color: #667eea;
        }}
        
        .stat-icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        
        .stat-number {{
            font-size: 3.5em;
            font-weight: bold;
            margin: 15px 0;
            line-height: 1;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }}
        
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .total {{ color: #007bff; }}
        .screens {{ color: #17a2b8; }}
        
        .content {{
            padding: 50px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .section-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 2em;
            margin: 0;
        }}
        
        .ai-insights {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 35px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        
        .ai-insights h3 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .ai-insights-content {{
            line-height: 1.8;
            color: #333;
            white-space: pre-line;
        }}
        
        .app-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .info-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }}
        
        .info-label {{
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .info-value {{
            color: #333;
            font-size: 1.1em;
        }}
        
        .features-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .feature-tag {{
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
        }}
        
        .bugs-list {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .bug-item {{
            padding: 10px 0;
            border-bottom: 1px solid #ffe69c;
            display: flex;
            align-items: start;
            gap: 10px;
        }}
        
        .bug-item:last-child {{
            border-bottom: none;
        }}
        
        .bug-icon {{
            color: #dc3545;
            font-size: 1.2em;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 40px;
            background: #e0e0e0;
            border-radius: 20px;
            overflow: hidden;
            margin: 25px 0;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.1em;
            transition: width 1.5s ease;
            box-shadow: 0 0 20px rgba(40, 167, 69, 0.4);
        }}
        
        .test-results {{
            display: grid;
            gap: 25px;
        }}
        
        .test-item {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s;
        }}
        
        .test-item:hover {{
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            transform: translateX(5px);
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .test-name {{
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            flex: 1;
        }}
        
        .test-status {{
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .ai-reasoning {{
            background: linear-gradient(to right, #667eea15, transparent);
            padding: 15px;
            border-left: 3px solid #667eea;
            margin: 15px 0;
            border-radius: 5px;
            font-style: italic;
            color: #555;
        }}
        
        .ai-reasoning::before {{
            content: '💭 AI Reasoning: ';
            font-weight: bold;
            color: #667eea;
            font-style: normal;
        }}
        
        .test-details {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 0.95em;
        }}
        
        .detail-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .detail-row:last-child {{
            border-bottom: none;
        }}
        
        .detail-label {{
            font-weight: 600;
            min-width: 150px;
            color: #555;
        }}
        
        .detail-value {{
            color: #333;
            flex: 1;
        }}
        
        .screenshot {{
            margin-top: 20px;
        }}
        
        .screenshot img {{
            max-width: 100%;
            max-height: 600px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: transform 0.3s;
        }}
        
        .screenshot img:hover {{
            transform: scale(1.02);
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 3px solid #667eea;
        }}
        
        .footer-content {{
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .powered-by {{
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .app-info {{
                grid-template-columns: 1fr;
            }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .test-item {{
            animation: fadeIn 0.5s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI-Powered Test Report</h1>
            <div class="subtitle">Intelligent Mobile App Testing with Gemini AI</div>
            <div class="ai-badge">✨ Powered by Google Gemini</div>
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.9;">
                {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-label">Total Tests</div>
                <div class="stat-number total">{total}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-label">Passed</div>
                <div class="stat-number passed">{passed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">❌</div>
                <div class="stat-label">Failed</div>
                <div class="stat-number failed">{failed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🖼️</div>
                <div class="stat-label">Screens</div>
                <div class="stat-number screens">{test_summary['screens_explored']}</div>
            </div>
        </div>
        
        <div class="content">
            <!-- AI Insights Section -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">🧠</div>
                    <h2>AI-Generated Insights</h2>
                </div>
                
                <div class="ai-insights">
                    <h3>🤖 Gemini Analysis</h3>
                    <div class="ai-insights-content">{ai_insights_html}</div>
                </div>
                
                {'<div class="bugs-list"><h4 style="margin-bottom: 15px; color: #856404;">⚠️ Potential Issues Detected</h4>' + ''.join(f'<div class="bug-item"><span class="bug-icon">🐛</span><span>{bug}</span></div>' for bug in potential_bugs) + '</div>' if potential_bugs else ''}
            </div>
            
            <!-- Test Performance -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">📈</div>
                    <h2>Test Performance</h2>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pass_rate}%">
                        {pass_rate:.1f}% Pass Rate
                    </div>
                </div>
            </div>
            
            <!-- App Information -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">📱</div>
                    <h2>Application Information</h2>
                </div>
                
                <div class="app-info">
                    <div class="info-card">
                        <div class="info-label">App Type</div>
                        <div class="info-value">{app_type}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Package Name</div>
                        <div class="info-value">{apk_info.get('package_name', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Main Activity</div>
                        <div class="info-value" style="word-break: break-all;">{apk_info.get('main_activity', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Screens Explored</div>
                        <div class="info-value">{test_summary['screens_explored']}</div>
                    </div>
                </div>
                
                {f'<div style="margin-top: 20px;"><div class="info-label">Identified Features</div><div class="features-list">' + ''.join(f'<span class="feature-tag">{feature}</span>' for feature in core_features[:10]) + '</div></div>' if core_features else ''}
            </div>
            
            <!-- Test Results -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">🧪</div>
                    <h2>Detailed Test Results</h2>
                </div>
                <div class="test-results">
"""
        
        # Add test results
        for i, result in enumerate(test_summary['test_results']):
            status_class = 'status-pass' if result['status'] == 'PASS' else 'status-fail'
            
            # AI reasoning
            reasoning_html = ""
            if result.get('ai_reasoning'):
                reasoning_html = f'<div class="ai-reasoning">{result["ai_reasoning"]}</div>'
            
            # Element details
            details_html = ""
            if result.get('details'):
                details = result['details']
                details_html = f"""
                <div class="test-details">
                    <div class="detail-row">
                        <span class="detail-label">Element Type:</span>
                        <span class="detail-value">{details.get('type', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Text:</span>
                        <span class="detail-value">{details.get('text', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Resource ID:</span>
                        <span class="detail-value">{details.get('resource_id', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Description:</span>
                        <span class="detail-value">{details.get('content_desc', 'N/A')}</span>
                    </div>
                </div>
"""
            
            # Screenshot
            screenshot_html = ""
            if result.get('screenshot'):
                screenshot_html = f"""
                <div class="screenshot">
                    <img src="../{result['screenshot']}" alt="Screenshot" loading="lazy">
                </div>
"""
            
            html += f"""
                    <div class="test-item" style="animation-delay: {i * 0.05}s;">
                        <div class="test-header">
                            <div class="test-name">{result['test_name']}</div>
                            <div class="test-status {status_class}">{result['status']}</div>
                        </div>
                        {reasoning_html}
                        {details_html}
                        {screenshot_html}
                    </div>
"""
        
        html += """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <p style="font-size: 1.1em; font-weight: 600; margin-bottom: 10px;">
                    🤖 AI-Powered Mobile App Testing Agent
                </p>
                <p class="powered-by">
                    Powered by Google Gemini AI | Python + Appium + ADB
                </p>
                <p style="margin-top: 10px; font-size: 0.85em;">
                    Generated automatically with intelligent test planning and execution
                </p>
            </div>
        </div>
    </div>
    
    <script>
        // Add click to enlarge for screenshots
        document.querySelectorAll('.screenshot img').forEach(img => {
            img.addEventListener('click', function() {
                window.open(this.src, '_blank');
            });
        });
        
        // Animate progress bar on load
        window.addEventListener('load', () => {
            const progressFill = document.querySelector('.progress-fill');
            if (progressFill) {
                const width = progressFill.style.width;
                progressFill.style.width = '0%';
                setTimeout(() => {
                    progressFill.style.width = width;
                }, 100);
            }
        });
    </script>
</body>
</html>
"""
        
        return html
    
    def _generate_json(self, test_summary, apk_info):
        """Generate JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_test_report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        report_data = {
            'apk_info': apk_info,
            'test_summary': test_summary,
            'timestamp': timestamp,
            'report_type': 'ai_powered'
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"JSON report generated: {filepath}")
        return str(filepath)