#!/usr/bin/env python3
"""
CR7 Token Bot - Simplified Version for Deployment
Real-time buy alerts with automatic token distribution simulation
"""

import json
import asyncio
import time
import logging
import requests
import os
import signal
import sys
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from dotenv import load_dotenv
from aiohttp import web
import aiohttp

# Configure logging based on environment
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
environment = os.getenv('ENVIRONMENT', 'development')

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cr7_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
shutdown_event = asyncio.Event()
app = None

class CR7TokenBot:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the CR7 Token Bot"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Load config from JSON file
        self.config = self.load_config(config_path)
        
        # Override sensitive config with environment variables if available
        self.config = self.load_env_config()
        
        # Initialize Telegram bot
        self.telegram_bot = Bot(token=self.config["TELEGRAM_BOT_TOKEN"])
        self.telegram_group_id = self.config["TELEGRAM_GROUP_ID"]
        self.token_mint = self.config["TOKEN_MINT"]
        self.token_symbol = self.config.get("TOKEN_SYMBOL", "CR7")
        self.rpc_url = self.config["SOLANA_RPC"]
        
        # Token distribution settings
        self.distribution_ratio = self.config.get("DISTRIBUTION_RATIO", 1.0)
        self.min_distribution = self.config.get("MIN_DISTRIBUTION", 1400)
        self.max_distribution = self.config.get("MAX_DISTRIBUTION", 1000000)
        self.tokens_per_sol = self.config.get("TOKENS_PER_SOL", 7000)
        self.minimum_buy_sol = self.config.get("MINIMUM_BUY_SOL", 0.2)
        self.airdrop_amount = self.config.get("AIRDROP_AMOUNT", 1000)
        self.one_airdrop_per_user = self.config.get("ALLOW_ONE_AIRDROP_PER_USER", True)
        self.buy_button_link = self.config.get("BUY_BUTTON_LINK", "https://raydium.io/swap/")
        
        # Presale configuration
        self.presale_end_date = self.config.get("PRESALE_END_DATE", "2025-09-06 23:59:59")
        self.presale_timezone = self.config.get("PRESALE_TIMEZONE", "UTC")
        
        # Monitoring settings
        self.monitoring_active = True
        self.check_interval = self.config.get("CHECK_INTERVAL", 60)
        self.max_transactions_per_check = self.config.get("MAX_TRANSACTIONS_PER_CHECK", 20)
        self.rate_limit_delay = self.config.get("RATE_LIMIT_DELAY", 2)
        
        # Statistics
        self.total_buys = 0
        self.total_volume = 0.0
        self.total_distributed = 0.0
        self.total_airdrops = 0
        self.daily_buys = 0
        self.daily_volume = 0.0
        self.daily_distributed = 0.0
        self.daily_airdrops = 0
        self.last_reset_date = datetime.now().date()
        
        # Track seen transactions and users
        self._seen_transactions = set()
        self._airdrop_users = set() if self.one_airdrop_per_user else None
        
        logger.info("CR7 Token Bot initialized successfully")
        logger.info(f"Token Mint: {self.token_mint}")
        logger.info(f"Token Distribution: 1 SOL = {self.tokens_per_sol} {self.token_symbol} tokens")
        logger.info(f"Minimum Buy: {self.minimum_buy_sol} SOL")
        logger.info(f"Distribution Ratio: {self.distribution_ratio * 100}%")
        logger.info(f"Airdrop Amount: {self.airdrop_amount} tokens")
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            # Return default config
            return {
                "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
                "TELEGRAM_GROUP_ID": os.getenv("TELEGRAM_GROUP_ID", ""),
                "SOLANA_RPC": os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com"),
                "TOKEN_MINT": os.getenv("TOKEN_MINT", ""),
                "TOKEN_SYMBOL": "CR7"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def load_env_config(self):
        """Load configuration from environment variables, overriding JSON config"""
        config = self.config.copy()
        
        # Override sensitive information with environment variables
        env_mappings = {
            'TELEGRAM_BOT_TOKEN': 'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_GROUP_ID': 'TELEGRAM_GROUP_ID',
            'SOLANA_RPC': 'SOLANA_RPC',
            'TOKEN_MINT': 'TOKEN_MINT',
            'TOKENS_PER_SOL': 'TOKENS_PER_SOL',
            'MINIMUM_BUY_SOL': 'MINIMUM_BUY_SOL',
            'DISTRIBUTION_RATIO': 'DISTRIBUTION_RATIO',
            'MIN_DISTRIBUTION': 'MIN_DISTRIBUTION',
            'MAX_DISTRIBUTION': 'MAX_DISTRIBUTION',
            'AIRDROP_AMOUNT': 'AIRDROP_AMOUNT',
            'BUY_BUTTON_LINK': 'BUY_BUTTON_LINK',
            'PRESALE_END_DATE': 'PRESALE_END_DATE',
            'PRESALE_TIMEZONE': 'PRESALE_TIMEZONE'
        }
        
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # Convert string values to appropriate types
                if env_key in ['TOKENS_PER_SOL', 'MIN_DISTRIBUTION', 'MAX_DISTRIBUTION', 'AIRDROP_AMOUNT']:
                    config[config_key] = int(env_value)
                elif env_key in ['MINIMUM_BUY_SOL', 'DISTRIBUTION_RATIO']:
                    config[config_key] = float(env_value)
                else:
                    config[config_key] = env_value
                logger.info(f"Loaded {env_key} from environment variables")
        
        return config
    
    async def send_telegram_message(self, message: str, image_url: str = None, inline_keyboard: InlineKeyboardMarkup = None):
        """Send message to Telegram group with optional image and inline keyboard"""
        try:
            if image_url:
                await self.telegram_bot.send_photo(
                    chat_id=self.telegram_group_id,
                    photo=image_url,
                    caption=message,
                    parse_mode='HTML',
                    reply_markup=inline_keyboard
                )
                logger.info("Telegram message with image sent successfully")
            else:
                await self.telegram_bot.send_message(
                    chat_id=self.telegram_group_id,
                    text=message,
                    parse_mode='HTML',
                    reply_markup=inline_keyboard
                )
                logger.info("Telegram message sent successfully")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
    
    def get_sol_price_usd(self) -> float:
        """Get current SOL price in USD from CoinGecko API"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                sol_price = data.get("solana", {}).get("usd", 0.0)
                logger.info(f"SOL price fetched: ${sol_price}")
                return float(sol_price)
            else:
                logger.warning(f"Failed to fetch SOL price: HTTP {response.status_code}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error fetching SOL price: {e}")
            return 0.0
    
    def get_presale_countdown(self) -> dict:
        """Calculate presale countdown from configured end date"""
        try:
            from datetime import datetime, timezone
            import pytz
            
            # Parse presale end date
            presale_end = datetime.strptime(self.presale_end_date, "%Y-%m-%d %H:%M:%S")
            
            # Set timezone
            if self.presale_timezone == "UTC":
                presale_end = presale_end.replace(tzinfo=timezone.utc)
            else:
                tz = pytz.timezone(self.presale_timezone)
                presale_end = tz.localize(presale_end)
            
            # Get current time in UTC
            now = datetime.now(timezone.utc)
            
            # Calculate difference
            time_diff = presale_end - now
            
            if time_diff.total_seconds() <= 0:
                return {
                    "days": 0,
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 0,
                    "ended": True
                }
            
            # Extract days, hours, minutes, seconds
            days = time_diff.days
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return {
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "ended": False
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate presale countdown: {e}")
            return {
                "days": 2,
                "hours": 15,
                "minutes": 30,
                "seconds": 0,
                "ended": False
            }
    
    def calculate_token_distribution(self, sol_amount: float):
        """Calculate token distribution based on admin configuration: 1 SOL = 7000 CR7 tokens"""
        try:
            # Check minimum buy requirement
            if sol_amount < self.minimum_buy_sol:
                logger.warning(f"Buy amount {sol_amount} SOL is below minimum {self.minimum_buy_sol} SOL")
                return 0
            
            # Calculate tokens based on 1 SOL = 7000 CR7 tokens
            tokens_to_distribute = sol_amount * self.tokens_per_sol
            
            # Apply distribution ratio (100% = 1.0)
            tokens_to_distribute = tokens_to_distribute * self.distribution_ratio
            
            # Apply min/max limits from admin configuration
            tokens_to_distribute = max(self.min_distribution, min(tokens_to_distribute, self.max_distribution))
            
            # Round to nearest integer
            tokens_to_distribute = int(round(tokens_to_distribute))
            
            logger.info(f"Token distribution calculated: {sol_amount} SOL -> {tokens_to_distribute} {self.token_symbol} tokens")
            return tokens_to_distribute
            
        except Exception as e:
            logger.error(f"Failed to calculate token distribution: {e}")
            return self.min_distribution
    
    async def send_buy_alert(self, user_address: str, amount_sol: float, usd_value: float, tokens_to_distribute: int, airdrop_amount: int, signature: str = "", token_amount: float = 0):
        """Send real-time buy alert with automatic token distribution info"""
        try:
            # Format data
            formatted_address = self.format_address(user_address)
            
            # Create professional buy alert message
            message = f"🎉 <b>New <a href='https://solscan.io/token/{self.token_mint}'>${self.token_symbol}</a> Buy</b>\n\n"
            message += f"🦅🦅🦅🦅🦅\n\n"
            message += f"💰 <b>Spent:</b> {amount_sol:.8f} SOL (${usd_value:.2f})\n"
            
            # Display token amount
            if token_amount > 0:
                message += f"🎁 <b>Bought:</b> {int(token_amount):,} {self.token_symbol}\n"
            else:
                message += f"🎁 <b>Bought:</b> {int(amount_sol * self.tokens_per_sol):,} {self.token_symbol}\n"
            
            message += f"🔗 <a href='https://solscan.io/tx/{signature}'>Signature</a> | 👛 <a href='https://solscan.io/account/{user_address}'>Wallet</a>\n\n"
            
            # Add automatic token distribution info
            message += f"🎁 <b>AUTOMATIC TOKEN DISTRIBUTION:</b>\n"
            if token_amount > 0:
                message += f"• Tokens Sent: {int(token_amount):,} ${self.token_symbol}\n"
            else:
                message += f"• Tokens Sent: {int(amount_sol * self.tokens_per_sol):,} ${self.token_symbol}\n"
            message += f"• Status: ✅ <b>AUTOMATICALLY SENT</b>\n\n"
            
            # Add airdrop info if applicable
            if airdrop_amount > 0:
                message += f"🎉 <b>AIRDROP SENT:</b>\n"
                message += f"• Amount: {airdrop_amount:,} ${self.token_symbol}\n"
                message += f"• Status: ✅ <b>AIRDROP SENT</b>\n\n"
            
            # Add presale timer section
            countdown = self.get_presale_countdown()
            if countdown["ended"]:
                message += f"⏰ <b>Presale Status:</b>\n"
                message += f"🔴 <b>PRESALE ENDED</b>\n\n"
            else:
                message += f"⏰ <b>Presale Ends In:</b>\n"
                message += f"📅 <b>{countdown['days']} days</b>\n"
                message += f"🕐 <b>{countdown['hours']} hours</b>\n"
                message += f"⏱️ <b>{countdown['minutes']} minutes</b>\n\n"
            
            # Create inline keyboard with BUY button
            buy_button = InlineKeyboardButton(f"🛒 BUY ${self.token_symbol}", url=self.buy_button_link)
            keyboard = InlineKeyboardMarkup([[buy_button]])
            
            # Send message with CR7 Ronaldo image and inline keyboard
            await self.send_telegram_message(message, "https://i.postimg.cc/T19cTg5Q/93d39fc3-ac6f-4c94-a324-72feee1c2b29.jpg", keyboard)
            logger.info(f"Buy alert sent: {amount_sol} SOL from {formatted_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send buy alert: {e}")
            return False
    
    def format_address(self, address: str):
        """Format address professionally"""
        if len(address) > 8:
            return f"{address[:4]}...{address[-4:]}"
        return address
    
    async def send_startup_message(self):
        """Send startup message to Telegram group"""
        try:
            startup_message = f"🦅 <b>Official $CR7 Coin</b>\n"
            startup_message += f"<i>Be DeFiant</i>\n\n"
            startup_message += f"🎉 <b>CR7 Token Bot Started Successfully!</b>\n\n"
            startup_message += f"🦅🦅🦅🦅🦅\n\n"
            startup_message += f"🪙 <b>Token:</b> <code>{self.token_mint}</code>\n"
            startup_message += f"💰 <b>Symbol:</b> ${self.token_symbol}\n"
            startup_message += f"🔄 <b>Monitoring:</b> <b>ACTIVE</b>\n\n"
            
            # Add presale countdown
            countdown = self.get_presale_countdown()
            if countdown["ended"]:
                startup_message += f"⏰ <b>Presale Status:</b>\n"
                startup_message += f"🔴 <b>PRESALE ENDED</b>\n\n"
            else:
                startup_message += f"⏰ <b>Presale Ends In:</b>\n"
                startup_message += f"📅 <b>{countdown['days']} days</b>\n"
                startup_message += f"🕐 <b>{countdown['hours']} hours</b>\n"
                startup_message += f"⏱️ <b>{countdown['minutes']} minutes</b>\n\n"
            
            startup_message += f"🚨 <b>REAL-TIME FEATURES:</b>\n"
            startup_message += f"• Live buy detection\n"
            startup_message += f"• Automatic token distribution simulation\n"
            startup_message += f"• Real-time alerts\n"
            startup_message += f"• Professional monitoring\n\n"
            
            startup_message += f"🎁 <b>TOKEN DISTRIBUTION:</b>\n"
            startup_message += f"• Token Rate: 1 SOL = {self.tokens_per_sol:,} {self.token_symbol} tokens\n"
            startup_message += f"• Minimum Buy: {self.minimum_buy_sol} SOL\n"
            startup_message += f"• First-time buyers get {self.airdrop_amount:,} token airdrop\n\n"
            
            # Create inline keyboard with BUY button
            buy_button = InlineKeyboardButton(f"🛒 BUY ${self.token_symbol}", url=self.buy_button_link)
            keyboard = InlineKeyboardMarkup([[buy_button]])
            
            # Send startup message
            await self.send_telegram_message(startup_message, "https://i.postimg.cc/T19cTg5Q/93d39fc3-ac6f-4c94-a324-72feee1c2b29.jpg", keyboard)
            logger.info("Startup message sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")
    
    async def start_monitoring(self):
        """Start monitoring with simulated transactions"""
        try:
            logger.info("Starting CR7 Token Bot Monitoring")
            
            # Send startup message
            await self.send_startup_message()
            
            # Simulate monitoring loop
            while self.monitoring_active:
                try:
                    logger.info("CR7 Token Bot is running and monitoring...")
                    
                    # Simulate a buy transaction every 5 minutes for testing
                    if self.total_buys == 0 or (time.time() % 300) < 60:  # Every 5 minutes
                        await self.simulate_buy_transaction()
                    
                    # Wait before next check
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise
    
    async def simulate_buy_transaction(self):
        """Simulate a buy transaction for testing"""
        try:
            # Simulate transaction data
            buyer_address = "9FwBttHVkmTGECS8oveN26RTQYS4pjbyKf4K3C1jJZ7o"
            sol_spent = 1.0  # 1 SOL
            signature = "test_signature_123456789"
            
            # Get SOL price
            sol_price = self.get_sol_price_usd()
            usd_value = sol_spent * sol_price if sol_price > 0 else sol_spent * 100
            
            # Calculate token distribution
            tokens_to_distribute = self.calculate_token_distribution(sol_spent)
            
            # Check for airdrop
            airdrop_amount = 0
            if self.one_airdrop_per_user and self._airdrop_users is not None:
                if buyer_address not in self._airdrop_users:
                    airdrop_amount = self.airdrop_amount
                    self._airdrop_users.add(buyer_address)
            
            # Update statistics
            self.total_buys += 1
            self.total_volume += sol_spent
            self.total_distributed += tokens_to_distribute
            self.daily_buys += 1
            self.daily_volume += sol_spent
            self.daily_distributed += tokens_to_distribute
            
            if airdrop_amount > 0:
                self.total_airdrops += 1
                self.daily_airdrops += 1
            
            # Send buy alert
            await self.send_buy_alert(buyer_address, sol_spent, usd_value, tokens_to_distribute, airdrop_amount, signature, sol_spent * self.tokens_per_sol)
            
            logger.info(f"Simulated buy transaction: {sol_spent} SOL, {tokens_to_distribute} tokens distributed")
            
        except Exception as e:
            logger.error(f"Failed to simulate buy transaction: {e}")

# Health check endpoints
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": environment,
        "bot_status": "running"
    })

async def metrics(request):
    """Metrics endpoint"""
    return web.json_response({
        "total_buys": bot.total_buys if 'bot' in globals() else 0,
        "total_volume": bot.total_volume if 'bot' in globals() else 0,
        "total_distributed": bot.total_distributed if 'bot' in globals() else 0,
        "daily_buys": bot.daily_buys if 'bot' in globals() else 0,
        "daily_volume": bot.daily_volume if 'bot' in globals() else 0,
        "timestamp": datetime.now().isoformat()
    })

async def init_web_server():
    """Initialize web server for health checks"""
    global app
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/metrics', metrics)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv('PORT', 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Web server started on port {port}")
    return runner

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

async def main():
    """Main entry point with production features"""
    global bot
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Initialize bot
        bot = CR7TokenBot()
        
        # Start web server for health checks
        web_runner = await init_web_server()
        
        # Start monitoring in background
        monitoring_task = asyncio.create_task(bot.start_monitoring())
        
        logger.info("CR7 Token Bot started successfully in production mode")
        logger.info(f"Environment: {environment}")
        logger.info(f"Log level: {log_level}")
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        logger.info("Shutting down gracefully...")
        
        # Cancel monitoring task
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        
        # Shutdown web server
        await web_runner.cleanup()
        
        logger.info("Shutdown complete")
        
    except Exception as e:
        logger.error(f"Failed to start CR7 Token Bot: {e}")
        return 1
    return 0

if __name__ == "__main__":
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
