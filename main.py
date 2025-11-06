"""
Main Application - AI-Powered Entry point
"""
import yaml
import sys
import argparse
from pathlib import Path
from loguru import logger

from app.emulator_manager import EmulatorManager
from app.apk_installer import APKInstaller
from app.ui_explorer import UIExplorer
from app.ai_agent_core import AITestingAgent
from app.ai_test_executor import AITestExecutor
from app.report_generator import ReportGenerator

def setup_logging(config):
    """Setup logging configuration"""
    logger.remove()
    
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config['logging']['level']
    )
    
    logger.add(
        config['logging']['file'],
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
        rotation="10 MB"
    )

def load_config(config_path="config/config.yaml"):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        sys.exit(1)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='🤖 AI-Powered Mobile App Testing Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --apk myapp.apk --ai-key YOUR_GEMINI_API_KEY
  python main.py --apk myapp.apk --ai-key YOUR_KEY --skip-emulator
  python main.py --apk myapp.apk --ai-key YOUR_KEY --config custom_config.yaml
        """
    )
    
    parser.add_argument(
        '--apk',
        required=True,
        help='Path to APK file to test'
    )
    
    parser.add_argument(
        '--ai-key',
        required=False,
        default='AIzaSyC41RoUNUYb_q6hJERw99DJr3f-oz2OMRc',
        help='Gemini API key for AI-powered testing'
    )
    
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--skip-emulator',
        action='store_true',
        help='Skip emulator startup (use if already running)'
    )
    
    parser.add_argument(
        '--disable-ai',
        action='store_true',
        help='Disable AI features (fallback to basic testing)'
    )
    
    args = parser.parse_args()
    
    # Validate APK
    if not Path(args.apk).exists():
        logger.error(f"APK file not found: {args.apk}")
        sys.exit(1)
    
    # Load config
    config = load_config(args.config)
    setup_logging(config)
    
    logger.info("=" * 60)
    logger.info("🤖 AI-Powered Mobile App Testing Agent")
    logger.info("=" * 60)
    
    # Initialize components
    emulator = EmulatorManager(config)
    apk_installer = APKInstaller(config)
    ui_explorer = UIExplorer(config)
    report_generator = ReportGenerator(config)
    
    # Initialize AI agent
    ai_enabled = not args.disable_ai and args.ai_key
    
    if ai_enabled:
        try:
            logger.info("🧠 Initializing AI Testing Agent with Gemini...")
            ai_agent = AITestingAgent(config, args.ai_key)
            test_executor = AITestExecutor(config, ui_explorer, apk_installer, ai_agent)
            logger.info("✓ AI Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI: {str(e)}")
            logger.warning("Falling back to basic testing mode")
            ai_enabled = False
            # Fallback to old executor
            from app.test_executor import TestExecutor
            test_executor = TestExecutor(config, ui_explorer, apk_installer)
    else:
        logger.info("ℹ️  Running in basic testing mode (AI disabled)")
        from app.test_executor import TestExecutor
        test_executor = TestExecutor(config, ui_explorer, apk_installer)
    
    try:
        # Step 1: Start emulator
        if not args.skip_emulator:
            logger.info("\n📱 Step 1: Starting Android Emulator...")
            if not emulator.start():
                logger.error("Failed to start emulator. Exiting.")
                sys.exit(1)
        else:
            logger.info("\n📱 Step 1: Using existing emulator...")
            if not emulator.is_running():
                logger.error("Emulator not running. Remove --skip-emulator flag.")
                sys.exit(1)
        
        # Step 2: Install APK
        logger.info("\n📦 Step 2: Installing APK...")
        if not apk_installer.install(args.apk):
            logger.error("Failed to install APK. Exiting.")
            emulator.stop()
            sys.exit(1)
        
        apk_installer.grant_permissions()
        
        # Step 3: Run AI-powered tests
        if ai_enabled:
            logger.info("\n🤖 Step 3: Running AI-Powered Automated Tests...")
            logger.info("    (AI will intelligently explore and test your app)")
        else:
            logger.info("\n🧪 Step 3: Running Automated Tests...")
        
        test_summary = test_executor.run_tests()
        
        # Step 4: Generate enhanced report
        logger.info("\n📊 Step 4: Generating Enhanced Test Report...")
        apk_info = {
            'package_name': apk_installer.package_name,
            'main_activity': apk_installer.main_activity,
            'apk_path': args.apk
        }
        
        report_path = report_generator.generate(test_summary, apk_info)
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ Testing Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Total Tests: {test_summary['total_tests']}")
        logger.info(f"✅ Passed: {test_summary['passed']}")
        logger.info(f"❌ Failed: {test_summary['failed']}")
        logger.info(f"🖼️  Screens Explored: {test_summary['screens_explored']}")
        
        if ai_enabled and 'ai_insights' in test_summary:
            logger.info("\n🧠 AI Insights Preview:")
            insights = test_summary['ai_insights']
            preview = insights[:200] + "..." if len(insights) > 200 else insights
            logger.info(preview)
            logger.info("    (Full insights available in report)")
        
        logger.info(f"\n📄 Report: {report_path}")
        logger.info("=" * 60)
        
        # Cleanup
        logger.info("\n🧹 Cleaning up...")
        apk_installer.stop()
        
        if not args.skip_emulator:
            emulator.stop()
        
        logger.info("\n✨ All done! Check the report for detailed results.")
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Testing interrupted by user")
        apk_installer.stop()
        if not args.skip_emulator:
            emulator.stop()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ An error occurred: {str(e)}")
        logger.exception("Full error details:")
        apk_installer.stop()
        if not args.skip_emulator:
            emulator.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()