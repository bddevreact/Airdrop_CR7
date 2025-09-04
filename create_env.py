#!/usr/bin/env python3
"""
Script to create .env file from env_template.txt
"""

import os
import shutil

def create_env_file():
    """Create .env file from env_template.txt"""
    print("🔧 Creating .env file from template...")
    print("=" * 50)
    
    # Check if env_template.txt exists
    if not os.path.exists('env_template.txt'):
        print("❌ env_template.txt not found!")
        print("💡 Make sure env_template.txt exists in the current directory")
        return False
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Operation cancelled")
            return False
    
    try:
        # Copy env_template.txt to .env
        shutil.copy('env_template.txt', '.env')
        print("✅ .env file created successfully!")
        print("🔒 Your sensitive information is now stored in .env file")
        print("⚠️  IMPORTANT: Keep .env file secure and never share it publicly!")
        print("📝 The bot will automatically use .env values over config.json values")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file()
