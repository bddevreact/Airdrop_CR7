#!/usr/bin/env python3
"""
Deployment verification script for CR7 Token Bot
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if requirements.txt is valid"""
    print("🔍 Checking requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Check for problematic packages
    problematic_packages = ['spl-token', 'solana', 'solders', 'anchorpy']
    
    for package in problematic_packages:
        if package in content:
            print(f"❌ Found problematic package: {package}")
            print("💡 Remove Solana SDK dependencies for easier deployment")
            return False
    
    print("✅ requirements.txt looks good!")
    return True

def check_env_file():
    """Check if .env file exists"""
    print("🔍 Checking .env file...")
    
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    elif os.path.exists('env_template.txt'):
        print("⚠️  .env file not found, but env_template.txt exists")
        print("💡 Copy env_template.txt to .env before deployment")
        return False
    else:
        print("❌ No environment configuration found!")
        return False

def check_main_py():
    """Check if main.py exists and is valid"""
    print("🔍 Checking main.py...")
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found!")
        return False
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for Solana SDK imports
    if 'from solana' in content or 'from spl' in content:
        print("⚠️  Found Solana SDK imports in main.py")
        print("💡 Make sure Solana SDK is disabled for deployment")
    
    print("✅ main.py found")
    return True

def test_imports():
    """Test if required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'requests',
        'telegram',
        'dotenv',
        'pytz'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'telegram':
                import telegram
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package} - OK")
        except ImportError as e:
            print(f"❌ {package} - FAILED: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("💡 Install missing packages: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages can be imported!")
    return True

def main():
    """Main deployment check"""
    print("🚀 CR7 Token Bot - Deployment Check")
    print("=" * 50)
    
    checks = [
        check_requirements,
        check_env_file,
        check_main_py,
        test_imports
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Push code to GitHub repository")
        print("2. Connect Railway to your repository")
        print("3. Set environment variables in Railway dashboard")
        print("4. Deploy and monitor logs")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("- Remove Solana SDK dependencies from requirements.txt")
        print("- Copy env_template.txt to .env")
        print("- Install missing packages: pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
