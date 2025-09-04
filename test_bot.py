#!/usr/bin/env python3
"""
Simple test script to verify CR7 Token Bot works without errors
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import json
        print("✅ json - OK")
        
        import asyncio
        print("✅ asyncio - OK")
        
        import time
        print("✅ time - OK")
        
        import logging
        print("✅ logging - OK")
        
        import requests
        print("✅ requests - OK")
        
        import os
        print("✅ os - OK")
        
        from datetime import datetime
        print("✅ datetime - OK")
        
        from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
        print("✅ telegram - OK")
        
        from telegram.error import TelegramError
        print("✅ telegram.error - OK")
        
        from dotenv import load_dotenv
        print("✅ dotenv - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_main_py():
    """Test if main.py can be imported without errors"""
    print("\n🔍 Testing main.py import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Try to import main module
        import main
        print("✅ main.py imported successfully")
        
        # Check if RealMonitoringBot class exists
        if hasattr(main, 'RealMonitoringBot'):
            print("✅ RealMonitoringBot class found")
        else:
            print("❌ RealMonitoringBot class not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing main.py: {e}")
        return False

def test_bot_initialization():
    """Test if bot can be initialized (without actually starting)"""
    print("\n🔍 Testing bot initialization...")
    
    try:
        import main
        
        # Create a minimal config for testing
        test_config = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_GROUP_ID": "test_group",
            "SOLANA_RPC": "https://api.mainnet-beta.solana.com",
            "TOKEN_MINT": "test_mint",
            "TOKEN_SYMBOL": "CR7",
            "DISTRIBUTION_RATIO": 1.0,
            "MIN_DISTRIBUTION": 1400,
            "MAX_DISTRIBUTION": 1000000,
            "TOKENS_PER_SOL": 7000,
            "MINIMUM_BUY_SOL": 0.2,
            "AIRDROP_AMOUNT": 1000,
            "ALLOW_ONE_AIRDROP_PER_USER": True,
            "BUY_BUTTON_LINK": "https://raydium.io/swap/",
            "PRESALE_END_DATE": "2025-09-06 23:59:59",
            "PRESALE_TIMEZONE": "UTC",
            "CHECK_INTERVAL": 60,
            "MAX_TRANSACTIONS_PER_CHECK": 20,
            "RATE_LIMIT_DELAY": 2
        }
        
        # Mock the config loading
        original_load_config = main.RealMonitoringBot.load_config
        main.RealMonitoringBot.load_config = lambda self, path: test_config
        
        # Try to create bot instance
        bot = main.RealMonitoringBot()
        print("✅ Bot initialized successfully")
        
        # Restore original method
        main.RealMonitoringBot.load_config = original_load_config
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing bot: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 CR7 Token Bot - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_main_py,
        test_bot_initialization
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! Bot is ready for deployment!")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
