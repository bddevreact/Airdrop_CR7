#!/usr/bin/env python3
"""
CR7 Token Bot - Production Testing Script
This script validates the production setup and configuration
"""

import os
import sys
import json
import requests
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionTester:
    def __init__(self):
        """Initialize the production tester"""
        load_dotenv()
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def log_error(self, message):
        """Log an error"""
        self.errors.append(message)
        logger.error(f"❌ {message}")
    
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        logger.warning(f"⚠️  {message}")
    
    def log_success(self, message):
        """Log a success"""
        self.passed.append(message)
        logger.info(f"✅ {message}")
    
    def test_environment_variables(self):
        """Test environment variables"""
        logger.info("🔍 Testing environment variables...")
        
        required_vars = {
            'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
            'TELEGRAM_GROUP_ID': 'Telegram group ID',
            'TOKEN_MINT': 'Token mint address',
            'SOLANA_RPC': 'Solana RPC URL'
        }
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value or value.startswith('your_') or value == '':
                self.log_error(f"Missing or invalid {description}: {var}")
            else:
                self.log_success(f"{description} is configured: {var}")
        
        # Test optional variables
        optional_vars = {
            'TOKENS_PER_SOL': '7000',
            'MINIMUM_BUY_SOL': '0.2',
            'AIRDROP_AMOUNT': '1000'
        }
        
        for var, default in optional_vars.items():
            value = os.getenv(var, default)
            try:
                if var in ['TOKENS_PER_SOL', 'AIRDROP_AMOUNT']:
                    int(value)
                else:
                    float(value)
                self.log_success(f"Optional variable {var} is valid: {value}")
            except ValueError:
                self.log_warning(f"Invalid value for {var}: {value}")
    
    def test_config_file(self):
        """Test configuration file"""
        logger.info("🔍 Testing configuration file...")
        
        if not os.path.exists('config.json'):
            self.log_error("config.json file not found")
            return
        
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Check for sensitive data
            sensitive_keys = ['TELEGRAM_BOT_TOKEN', 'WALLET_PRIVATE_KEY']
            for key in sensitive_keys:
                if key in config and config[key] and config[key] != "" and config[key] != []:
                    if key == 'TELEGRAM_BOT_TOKEN' and not config[key].startswith('your_'):
                        self.log_warning(f"Sensitive data found in config.json: {key}")
                    elif key == 'WALLET_PRIVATE_KEY' and config[key] != []:
                        self.log_warning(f"Sensitive data found in config.json: {key}")
            
            self.log_success("Configuration file is valid")
            
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON in config.json: {e}")
        except Exception as e:
            self.log_error(f"Error reading config.json: {e}")
    
    def test_dependencies(self):
        """Test Python dependencies"""
        logger.info("🔍 Testing Python dependencies...")
        
        required_packages = [
            'requests',
            'telegram',
            'dotenv',
            'pytz',
            'aiohttp'
        ]
        
        for package in required_packages:
            try:
                if package == 'telegram':
                    import telegram
                elif package == 'dotenv':
                    import dotenv
                else:
                    __import__(package)
                self.log_success(f"Package {package} is available")
            except ImportError as e:
                self.log_error(f"Package {package} not available: {e}")
    
    def test_telegram_connection(self):
        """Test Telegram bot connection"""
        logger.info("🔍 Testing Telegram bot connection...")
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token or token.startswith('your_'):
            self.log_error("Telegram bot token not configured")
            return
        
        try:
            from telegram import Bot
            bot = Bot(token=token)
            
            # Test bot info
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            bot_info = loop.run_until_complete(bot.get_me())
            loop.close()
            
            self.log_success(f"Telegram bot connected: @{bot_info.username}")
            
        except Exception as e:
            self.log_error(f"Failed to connect to Telegram: {e}")
    
    def test_solana_rpc(self):
        """Test Solana RPC connection"""
        logger.info("🔍 Testing Solana RPC connection...")
        
        rpc_url = os.getenv('SOLANA_RPC', 'https://api.mainnet-beta.solana.com')
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getHealth"
            }
            
            response = requests.post(rpc_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.log_success(f"Solana RPC is accessible: {rpc_url}")
            else:
                self.log_warning(f"Solana RPC returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Failed to connect to Solana RPC: {e}")
    
    def test_web_server(self):
        """Test web server endpoints"""
        logger.info("🔍 Testing web server endpoints...")
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"Health endpoint working: {data.get('status')}")
            else:
                self.log_warning(f"Health endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("Web server not running (this is normal if not started yet)")
        except Exception as e:
            self.log_error(f"Health endpoint error: {e}")
        
        # Test metrics endpoint
        try:
            response = requests.get(f"{base_url}/metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_success("Metrics endpoint working")
            else:
                self.log_warning(f"Metrics endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_warning("Web server not running (this is normal if not started yet)")
        except Exception as e:
            self.log_error(f"Metrics endpoint error: {e}")
    
    def test_file_structure(self):
        """Test required file structure"""
        logger.info("🔍 Testing file structure...")
        
        required_files = [
            'main_simple.py',
            'requirements.txt',
            'Dockerfile',
            'docker-compose.yml',
            'config.json'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                self.log_success(f"Required file exists: {file}")
            else:
                self.log_error(f"Required file missing: {file}")
        
        # Check for logs directory
        if os.path.exists('logs'):
            self.log_success("Logs directory exists")
        else:
            self.log_warning("Logs directory not found (will be created on startup)")
    
    def run_all_tests(self):
        """Run all production tests"""
        logger.info("🚀 Starting CR7 Token Bot Production Tests")
        logger.info("=" * 50)
        
        tests = [
            self.test_file_structure,
            self.test_dependencies,
            self.test_config_file,
            self.test_environment_variables,
            self.test_telegram_connection,
            self.test_solana_rpc,
            self.test_web_server
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_error(f"Test {test.__name__} failed with exception: {e}")
            logger.info("")
        
        # Print summary
        logger.info("=" * 50)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 50)
        
        logger.info(f"✅ Passed: {len(self.passed)}")
        logger.info(f"⚠️  Warnings: {len(self.warnings)}")
        logger.info(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            logger.info("\n❌ ERRORS:")
            for error in self.errors:
                logger.info(f"  - {error}")
        
        if self.warnings:
            logger.info("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                logger.info(f"  - {warning}")
        
        if not self.errors:
            logger.info("\n🎉 All critical tests passed! Ready for production!")
            return True
        else:
            logger.info("\n❌ Some tests failed. Please fix the errors above.")
            return False

def main():
    """Main entry point"""
    tester = ProductionTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
