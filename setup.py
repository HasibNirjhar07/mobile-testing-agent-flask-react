"""
Setup script for Automated Mobile App Testing Agent
Helps verify installation and setup
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Check Python version"""
    print("\n📦 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need 3.9+")
        return False

def check_command(command, name):
    """Check if command exists"""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ {name} - OK")
            return True
        else:
            print(f"❌ {name} - Not found")
            return False
    except FileNotFoundError:
        print(f"❌ {name} - Not found")
        return False
    except Exception as e:
        print(f"❌ {name} - Error: {str(e)}")
        return False

def check_adb():
    """Check ADB"""
    print("\n🔧 Checking ADB (Android Debug Bridge)...")
    return check_command("adb", "ADB")

def check_aapt():
    """Check AAPT"""
    print("\n🔧 Checking AAPT (Android Asset Packaging Tool)...")
    return check_command("aapt", "AAPT")

def check_emulator():
    """Check Android Emulator"""
    print("\n📱 Checking Android Emulator...")
    try:
        result = subprocess.run(
            ["emulator", "-list-avds"],
            capture_output=True,
            text=True,
            timeout=5
        )
        avds = result.stdout.strip().split('\n')
        if avds and avds[0]:
            print(f"✅ Found {len(avds)} emulator(s):")
            for avd in avds:
                print(f"   - {avd}")
            return True
        else:
            print("❌ No emulators found")
            return False
    except FileNotFoundError:
        print("❌ Emulator command not found")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_android_home():
    """Check ANDROID_HOME environment variable"""
    print("\n🌍 Checking ANDROID_HOME...")
    android_home = os.environ.get('ANDROID_HOME')
    if android_home:
        print(f"✅ ANDROID_HOME: {android_home}")
        if Path(android_home).exists():
            print("✅ Directory exists")
            return True
        else:
            print("❌ Directory does not exist")
            return False
    else:
        print("❌ ANDROID_HOME not set")
        return False

def check_directories():
    """Check required directories"""
    print("\n📁 Checking directories...")
    dirs = ['app', 'config', 'tests', 'reports', 'screenshots']
    all_ok = True
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ - OK")
        else:
            print(f"❌ {dir_name}/ - Missing (creating...)")
            dir_path.mkdir(exist_ok=True)
            all_ok = False
    
    return all_ok

def check_config():
    """Check configuration file"""
    print("\n⚙️  Checking configuration...")
    config_path = Path("config/config.yaml")
    if config_path.exists():
        print("✅ config.yaml - OK")
        return True
    else:
        print("❌ config.yaml - Missing")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✅ Dependencies installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {str(e)}")
        return False

def run_diagnostics():
    """Run all diagnostic checks"""
    print_header("🔍 Automated Mobile App Testing Agent - Setup Verification")
    
    results = {
        "Python": check_python(),
        "ADB": check_adb(),
        "AAPT": check_aapt(),
        "Emulator": check_emulator(),
        "ANDROID_HOME": check_android_home(),
        "Directories": check_directories(),
        "Config": check_config()
    }
    
    print_header("📊 Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, status in results.items():
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"{name:20} {status_str}")
    
    print(f"\nScore: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✨ All checks passed! You're ready to go!")
        print("\nRun your first test:")
        print("  python main.py --apk your_app.apk")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        
        if not results["ANDROID_HOME"]:
            print("\n1. Set ANDROID_HOME:")
            print("   export ANDROID_HOME=$HOME/Android/Sdk  # Linux/macOS")
            print("   setx ANDROID_HOME \"C:\\Android\\Sdk\"  # Windows")
        
        if not results["ADB"] or not results["AAPT"]:
            print("\n2. Add Android SDK to PATH:")
            print("   export PATH=$PATH:$ANDROID_HOME/platform-tools")
            print("   export PATH=$PATH:$ANDROID_HOME/build-tools/33.0.0")
        
        if not results["Emulator"]:
            print("\n3. Create an emulator:")
            print("   - Open Android Studio")
            print("   - Tools → AVD Manager")
            print("   - Create Virtual Device")
            print("   - Name it: test_device")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup and verify installation")
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install Python dependencies'
    )
    
    args = parser.parse_args()
    
    if args.install:
        install_dependencies()
    
    run_diagnostics()

if __name__ == "__main__":
    main()