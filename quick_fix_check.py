"""
Quick Fix Verification Script
Run this after setting environment variables
"""
import os
import subprocess
import sys

print("=" * 60)
print("🔧 Environment Fix Verification")
print("=" * 60)

# Check ANDROID_HOME
print("\n1. Checking ANDROID_HOME...")
android_home = os.environ.get('ANDROID_HOME')
if android_home:
    print(f"   ✅ ANDROID_HOME = {android_home}")
    
    # Check if path exists
    if os.path.exists(android_home):
        print(f"   ✅ Path exists")
    else:
        print(f"   ❌ Path does not exist!")
        print(f"   Please check the path: {android_home}")
else:
    print("   ❌ ANDROID_HOME not found!")
    print("\n   SOLUTION:")
    print("   1. Close PowerShell completely")
    print("   2. Reopen PowerShell")
    print("   3. Run this script again")
    sys.exit(1)

# Check emulator
print("\n2. Checking emulator...")
emulator_path = os.path.join(android_home, 'emulator', 'emulator.exe')
if os.path.exists(emulator_path):
    print(f"   ✅ Emulator found at: {emulator_path}")
else:
    print(f"   ❌ Emulator not found at: {emulator_path}")

# Check ADB
print("\n3. Checking ADB...")
try:
    result = subprocess.run(
        ["adb", "version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print("   ✅ ADB is working")
    else:
        print("   ❌ ADB failed")
except FileNotFoundError:
    print("   ❌ ADB not in PATH")
    print(f"\n   Add this to System PATH:")
    print(f"   {os.path.join(android_home, 'platform-tools')}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Check available emulators
print("\n4. Checking available emulators...")
try:
    result = subprocess.run(
        ["emulator", "-list-avds"],
        capture_output=True,
        text=True,
        timeout=10
    )
    avds = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    
    if avds:
        print("   ✅ Found emulators:")
        for avd in avds:
            print(f"      - {avd}")
        
        print(f"\n   📝 Update config.yaml with one of these names")
    else:
        print("   ❌ No emulators found")
        print("\n   Create one in Android Studio:")
        print("   Tools → Device Manager → Create Device")
        
except FileNotFoundError:
    print("   ❌ Emulator command not found")
    print(f"\n   Add this to System PATH:")
    print(f"   {os.path.join(android_home, 'emulator')}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)

if android_home and os.path.exists(emulator_path):
    print("✅ Environment is configured correctly!")
    print("\nYou can now run:")
    print("   python main.py --apk tests/sample_apks/your_app.apk")
else:
    print("⚠️  Please complete the setup steps above")
    print("\nIf you just set environment variables:")
    print("1. Close ALL PowerShell/Command Prompt windows")
    print("2. Open a NEW PowerShell window")
    print("3. Run this script again")

print("=" * 60)