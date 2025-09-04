#!/usr/bin/env python3
"""
Test script to verify .env configuration is working
"""

import os
from dotenv import load_dotenv

def test_env_config():
    """Test if .env file is loaded correctly"""
    print("🔍 Testing .env configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test key environment variables
    env_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_GROUP_ID', 
        'SOLANA_RPC',
        'TOKEN_MINT',
        'WALLET_PRIVATE_KEY',
        'TOKENS_PER_SOL',
        'MINIMUM_BUY_SOL',
        'DISTRIBUTION_RATIO',
        'MIN_DISTRIBUTION',
        'MAX_DISTRIBUTION',
        'AIRDROP_AMOUNT',
        'BUY_BUTTON_LINK',
        'PRESALE_END_DATE',
        'PRESALE_TIMEZONE'
    ]
    
    print("📋 Environment Variables Status:")
    print("-" * 30)
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive information
            if 'TOKEN' in var or 'KEY' in var:
                masked_value = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not found")
    
    print("\n" + "=" * 50)
    
    # Test if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("💡 Create .env file by copying env_template.txt:")
        print("   cp env_template.txt .env")
    
    print("\n🚀 Configuration Test Complete!")

if __name__ == "__main__":
    test_env_config()
