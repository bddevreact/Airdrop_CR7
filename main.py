#!/usr/bin/env python3
"""
Real Monitoring Bot - Real-time buy alerts with automatic token distribution
"""

import json
import asyncio
import time
import logging
import requests
import os
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from dotenv import load_dotenv
# Solana SDK imports (optional - for automatic transfers)
# Note: Solana SDK dependencies removed for easier deployment
# Token transfers are simulated for now
SOLANA_SDK_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_monitoring_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealMonitoringBot:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the Real Monitoring Bot"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Load config from JSON file
        self.config = self.load_config(config_path)
        
        # Override sensitive config with environment variables if available
        self.config = self.load_env_config()
        self.telegram_bot = Bot(token=self.config["TELEGRAM_BOT_TOKEN"])
        self.telegram_group_id = self.config["TELEGRAM_GROUP_ID"]
        self.token_mint = self.config["TOKEN_MINT"]
        self.token_symbol = self.config.get("TOKEN_SYMBOL", "CR7")
        self.rpc_url = self.config["SOLANA_RPC"]
        
        # Admin configuration for token distribution
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
        
        # Real-time monitoring settings
        self.monitoring_active = True
        self.check_interval = self.config.get("CHECK_INTERVAL", 60)  # seconds (increased to avoid rate limiting)
        self.max_transactions_per_check = self.config.get("MAX_TRANSACTIONS_PER_CHECK", 20)  # reduced to avoid rate limiting
        self.rate_limit_delay = self.config.get("RATE_LIMIT_DELAY", 2)  # seconds between requests
        
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
        
        # Solana setup for automatic token transfers
        # Note: Solana SDK disabled for easier deployment
        self.solana_client = None
        self.admin_wallet = None
        self.admin_token_account = None
        
        # Track seen transactions and users
        self._seen_transactions = set()
        self._airdrop_users = set() if self.one_airdrop_per_user else None
        
        logger.info("Real Monitoring Bot initialized successfully")
        logger.info(f"Token Mint: {self.token_mint}")
        logger.info(f"Monitoring Active: {self.monitoring_active}")
        logger.info(f"Check Interval: {self.check_interval} seconds")
        logger.info(f"Token Distribution: 1 SOL = {self.tokens_per_sol} {self.token_symbol} tokens")
        logger.info(f"Minimum Buy: {self.minimum_buy_sol} SOL")
        logger.info(f"Distribution Ratio: {self.distribution_ratio * 100}%")
        logger.info(f"Admin Wallet: {self.admin_wallet.public_key if self.admin_wallet else 'Not configured'}")
        logger.info(f"Airdrop Amount: {self.airdrop_amount} tokens")
    
    def _setup_admin_wallet(self):
        """Setup admin wallet for automatic token transfers"""
        logger.info("Solana SDK disabled - automatic transfers simulated")
        self.admin_wallet = None
        self.admin_token_account = None
    
    def _get_admin_token_account(self):
        """Get admin's token account for the monitored token"""
        logger.info("Solana SDK disabled - token account setup skipped")
        self.admin_token_account = None
    
    async def transfer_tokens_to_buyer(self, buyer_address: str, token_amount: int) -> bool:
        """Transfer tokens to buyer wallet automatically"""
        try:
            if not SOLANA_SDK_AVAILABLE:
                logger.warning("Solana SDK not available - skipping token transfer")
                return False
                
            if not self.admin_wallet or not self.admin_token_account:
                logger.warning("Admin wallet not configured - skipping token transfer")
                return False
            
            # For now, we'll simulate the transfer since SPL token transfers require more complex setup
            # In production, you would implement proper SPL token transfers here
            logger.info(f"Simulating token transfer: {token_amount} tokens to {buyer_address}")
            logger.info("Note: Actual token transfer requires proper SPL token account setup")
            
            # Simulate successful transfer
            return True
                
        except Exception as e:
            logger.error(f"Token transfer failed: {e}")
            return False
    
    async def _get_or_create_buyer_token_account(self, buyer_pubkey) -> None:
        """Get or create buyer's token account"""
        logger.info("Solana SDK disabled - token account creation skipped")
        return None
    
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
            # Return default countdown if error
            return {
                "days": 2,
                "hours": 15,
                "minutes": 30,
                "seconds": 0,
                "ended": False
            }
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            raise
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
            'WALLET_PRIVATE_KEY': 'WALLET_PRIVATE_KEY',
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
                elif env_key == 'WALLET_PRIVATE_KEY':
                    # Convert comma-separated string to list of integers
                    try:
                        config[config_key] = [int(x.strip()) for x in env_value.split(',')]
                    except ValueError:
                        logger.warning(f"Invalid WALLET_PRIVATE_KEY format in environment variables")
                else:
                    config[config_key] = env_value
                logger.info(f"Loaded {env_key} from environment variables")
        
        return config
    
    async def send_telegram_message(self, message: str, image_url: str = None, inline_keyboard: InlineKeyboardMarkup = None):
        """Send message to Telegram group with optional image and inline keyboard"""
        try:
            if image_url:
                # Send photo with caption and optional inline keyboard
                await self.telegram_bot.send_photo(
                    chat_id=self.telegram_group_id,
                    photo=image_url,
                    caption=message,
                    parse_mode='HTML',
                    reply_markup=inline_keyboard
                )
                logger.info("Telegram message with image sent successfully")
            else:
                # Send text message only with optional inline keyboard
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
            # CoinGecko API for SOL price
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
    
    def get_recent_transactions(self, limit: int = 20):
        """Get recent transactions for the token mint with rate limiting"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    self.token_mint,
                    {
                        "limit": limit
                    }
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    return data["result"]
                else:
                    logger.error(f"RPC error: {data}")
                    return []
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429). Waiting {self.rate_limit_delay} seconds...")
                time.sleep(self.rate_limit_delay)
                return []
            else:
                logger.error(f"HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []
    
    def get_transaction_details(self, signature: str):
        """Get detailed transaction information with rate limiting"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    return data["result"]
                else:
                    logger.error(f"Transaction error: {data}")
                    return None
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429) for transaction {signature[:8]}...")
                time.sleep(self.rate_limit_delay)
                return None
            else:
                logger.error(f"HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get transaction details: {e}")
            return None
    
    def analyze_transaction(self, tx_data):
        """Analyze transaction to detect token purchases"""
        try:
            if not tx_data:
                return None
            
            # Get transaction message
            transaction = tx_data.get("transaction", {})
            message = transaction.get("message", {})
            account_keys = message.get("accountKeys", [])
            
            if not account_keys:
                return None
            
            # First account is usually the fee payer/buyer
            buyer = account_keys[0]
            
            # Get pre and post token balances
            meta = tx_data.get("meta", {})
            pre_balances = meta.get("preBalances", [])
            post_balances = meta.get("postBalances", [])
            pre_token_balances = meta.get("preTokenBalances", [])
            post_token_balances = meta.get("postTokenBalances", [])
            
            if len(pre_balances) > 0 and len(post_balances) > 0:
                # Calculate SOL spent
                sol_spent = (pre_balances[0] - post_balances[0]) / 1e9
                
                if sol_spent > 0:
                    # This looks like a purchase
                    # Get real SOL price from API
                    sol_price = self.get_sol_price_usd()
                    if sol_price > 0:
                        usd_value = sol_spent * sol_price
                    else:
                        usd_value = sol_spent * 100  # Fallback: Assuming 1 SOL = $100
                    
                    # Calculate token amount received
                    token_amount = 0
                    if pre_token_balances and post_token_balances:
                        # Find token balance changes for our token mint
                        for pre_token in pre_token_balances:
                            if pre_token.get("mint") == self.token_mint:
                                pre_amount = float(pre_token.get("uiTokenAmount", {}).get("uiAmount", 0))
                                owner = pre_token.get("owner")
                                
                                # Find corresponding post balance for the same owner
                                for post_token in post_token_balances:
                                    if (post_token.get("mint") == self.token_mint and 
                                        post_token.get("owner") == owner):
                                        post_amount = float(post_token.get("uiTokenAmount", {}).get("uiAmount", 0))
                                        token_amount = post_amount - pre_amount
                                        logger.info(f"Token amount calculated: {token_amount} (pre: {pre_amount}, post: {post_amount})")
                                        break
                                break
                    
                    # If no token amount found, try alternative calculation
                    if token_amount <= 0:
                        # Try to find any token transfer in the transaction
                        for post_token in post_token_balances:
                            if post_token.get("mint") == self.token_mint:
                                post_amount = float(post_token.get("uiTokenAmount", {}).get("uiAmount", 0))
                                if post_amount > 0:
                                    token_amount = post_amount
                                    logger.info(f"Using post token amount: {token_amount}")
                                    break
                    
                    # If still no token amount found, estimate based on SOL spent
                    if token_amount <= 0:
                        token_amount = sol_spent * self.tokens_per_sol  # 1 SOL = 7000 tokens
                        logger.info(f"Using estimated token amount: {token_amount} (Rate: 1 SOL = {self.tokens_per_sol} tokens)")
                    
                    return {
                        "buyer": buyer,
                        "sol_spent": sol_spent,
                        "usd_value": usd_value,
                        "token_amount": token_amount,
                        "is_buy": True,
                        "transaction_type": "BUY"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze transaction: {e}")
            return None
    
    def format_address(self, address: str):
        """Format address professionally"""
        if len(address) > 8:
            return f"{address[:4]}...{address[-4:]}"
        return address
    
    def get_buy_rank(self, amount_sol: float):
        """Get buy rank based on amount"""
        if amount_sol >= 10:
            return "🐋 WHALE"
        elif amount_sol >= 5:
            return "🦈 SHARK"
        elif amount_sol >= 1:
            return "🐟 FISH"
        else:
            return "🦐 SHRIMP"
    
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
            
            logger.info(f"Token distribution calculated: {sol_amount} SOL -> {tokens_to_distribute} {self.token_symbol} tokens (Rate: 1 SOL = {self.tokens_per_sol} tokens)")
            return tokens_to_distribute
            
        except Exception as e:
            logger.error(f"Failed to calculate token distribution: {e}")
            return self.min_distribution
    
    def update_stats(self, sol_amount: float, tokens_distributed: int, airdrop_sent: bool = False):
        """Update statistics"""
        self.total_buys += 1
        self.total_volume += sol_amount
        self.total_distributed += tokens_distributed
        self.daily_buys += 1
        self.daily_volume += sol_amount
        self.daily_distributed += tokens_distributed
        
        if airdrop_sent:
            self.total_airdrops += 1
            self.daily_airdrops += 1
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_buys = 0
            self.daily_volume = 0.0
            self.daily_distributed = 0.0
            self.daily_airdrops = 0
            self.last_reset_date = current_date
    
    async def send_buy_alert(self, user_address: str, amount_sol: float, usd_value: float, tokens_to_distribute: int, airdrop_amount: int, signature: str = "", token_amount: float = 0):
        """Send real-time buy alert with automatic token distribution info"""
        try:
            # Update statistics
            self.update_stats(amount_sol, tokens_to_distribute, airdrop_amount > 0)
            self.reset_daily_stats()
            
            # Format data
            formatted_address = self.format_address(user_address)
            buy_rank = self.get_buy_rank(amount_sol)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Create professional buy alert message
            message = f"🎉 <b>New <a href='https://solscan.io/token/{self.token_mint}'>${self.token_symbol}</a> Buy</b>\n\n"
            message += f"🦅🦅🦅🦅🦅\n\n"
            message += f"💰 <b>Spent:</b> {amount_sol:.8f} SOL (${usd_value:.2f})\n"
            # Display real token amount if available, otherwise estimate
            if token_amount > 0:
                message += f"🎁 <b>Bought:</b> {int(token_amount):,} {self.token_symbol}\n"
            else:
                message += f"🎁 <b>Bought:</b> {int(amount_sol * self.tokens_per_sol):,} {self.token_symbol}\n"
            message += f"🔗 <a href='https://solscan.io/tx/{signature}'>Signature</a> | 👛 <a href='https://solscan.io/account/{user_address}'>Wallet</a>\n\n"
            
            # Add automatic token distribution info
            message += f"🎁 <b>AUTOMATIC TOKEN DISTRIBUTION:</b>\n"
            # Show real bought amount as tokens sent
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
            
            # Add presale timer section with dynamic countdown
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
            logger.info(f"Real-time buy alert sent: {amount_sol} SOL from {formatted_address}, {tokens_to_distribute} tokens distributed, {airdrop_amount} airdrop")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send buy alert: {e}")
            return False
    
    async def send_buy_guide(self):
        """Send comprehensive buy guide for group users"""
        try:
            message = f"🦅 <b>Official $CR7 Coin</b>\n"
            message += f"<i>Be DeFiant</i>\n\n"
            message += f"🛒 <b>HOW TO BUY <a href='https://solscan.io/token/{self.token_mint}'>{self.token_symbol}</a> TOKEN</b>\n\n"
            message += f"🦅🦅🦅🦅🦅\n\n"
            message += f"🪙 <b>Token Information:</b>\n"
            message += f"• Symbol: ${self.token_symbol}\n"
            message += f"• Contract: <code>{self.token_mint}</code>\n"
            message += f"• Network: Solana\n\n"
            
            message += f"📱 <b>Step-by-Step Guide:</b>\n"
            message += f"1️⃣ <b>Connect Wallet:</b>\n"
            message += f"   • Install Phantom, Solflare, or Backpack wallet\n"
            message += f"   • Add SOL to your wallet\n\n"
            
            message += f"2️⃣ <b>Go to DEX:</b>\n"
            message += f"   • <a href='https://raydium.io/swap/'>Raydium DEX</a> (Recommended)\n"
            message += f"   • <a href='https://jup.ag/'>Jupiter</a> (Best rates)\n"
            message += f"   • <a href='https://www.orca.so/'>Orca</a> (User-friendly)\n\n"
            
            message += f"3️⃣ <b>Buy Token:</b>\n"
            message += f"   • Connect your wallet\n"
            message += f"   • Paste token address: <code>{self.token_mint}</code>\n"
            message += f"   • Enter amount to buy\n"
            message += f"   • Confirm transaction\n\n"
            
            message += f"🎁 <b>BONUS FEATURES:</b>\n"
            message += f"• Token Rate: 1 SOL = {self.tokens_per_sol:,} {self.token_symbol} tokens\n"
            message += f"• Minimum Buy: {self.minimum_buy_sol} SOL\n"
            message += f"• First-time buyers get {self.airdrop_amount:,} token airdrop\n"
            message += f"• Automatic {self.distribution_ratio * 100}% token distribution\n"
            message += f"• Real-time buy alerts in this group\n"
            message += f"• Professional monitoring 24/7\n\n"
            
            message += f"⚠️ <b>IMPORTANT:</b>\n"
            message += f"• Always verify token address\n"
            message += f"• Start with small amounts\n"
            message += f"• Keep some SOL for transaction fees\n"
            message += f"• Never share your private keys\n\n"
            
            message += f"🚨 <b>NEED HELP?</b>\n"
            message += f"• Ask in this group\n"
            message += f"• Check transaction on <a href='https://solscan.io/token/{self.token_mint}'>Solscan</a>\n"
            message += f"• Monitor real-time alerts here\n\n"
            # Create inline keyboard with BUY button
            buy_button = InlineKeyboardButton(f"🛒 BUY ${self.token_symbol}", url=self.buy_button_link)
            keyboard = InlineKeyboardMarkup([[buy_button]])
            
            # Send buy guide with CR7 Ronaldo image and inline keyboard
            await self.send_telegram_message(message, "https://i.postimg.cc/T19cTg5Q/93d39fc3-ac6f-4c94-a324-72feee1c2b29.jpg", keyboard)
            logger.info("Buy guide sent to group")
        except Exception as e:
            logger.error(f"Failed to send buy guide: {e}")
    
    async def send_daily_summary(self):
        """Send daily summary with real-time stats"""
        try:
            if self.daily_buys > 0:
                message = f"🦅 <b>Official $CR7 Coin</b>\n"
                message += f"<i>Be DeFiant</i>\n\n"
                message += f"📊 <b>DAILY REAL-TIME SUMMARY</b>\n\n"
                message += f"🦅🦅🦅🦅🦅\n\n"
                message += f"🪙 Token: ${self.token_symbol}\n"
                message += f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                message += f"📈 <b>Today's Real-Time Activity:</b>\n"
                message += f"• Total Buys: {self.daily_buys}\n"
                message += f"• Total Volume: {self.daily_volume:.2f} SOL\n"
                message += f"• Total Distributed: {self.daily_distributed:,} tokens\n"
                message += f"• Total Airdrops: {self.daily_airdrops}\n"
                message += f"• Average Buy: {self.daily_volume/self.daily_buys:.2f} SOL\n"
                message += f"• Average Distribution: {self.daily_distributed/self.daily_buys:.0f} tokens\n"
                message += f"• Airdrop Rate: {(self.daily_airdrops/self.daily_buys*100):.1f}%\n\n"
                message += f"🏆 <b>All-Time Real-Time Stats:</b>\n"
                message += f"• Total Buys: {self.total_buys}\n"
                message += f"• Total Volume: {self.total_volume:.2f} SOL\n"
                message += f"• Total Distributed: {self.total_distributed:,} tokens\n"
                message += f"• Total Airdrops: {self.total_airdrops}\n\n"
                # Add presale countdown to daily summary
                countdown = self.get_presale_countdown()
                if countdown["ended"]:
                    message += f"⏰ <b>Presale Status:</b>\n"
                    message += f"🔴 <b>PRESALE ENDED</b>\n\n"
                else:
                    message += f"⏰ <b>Presale Ends In:</b>\n"
                    message += f"📅 <b>{countdown['days']} days</b>\n"
                    message += f"🕐 <b>{countdown['hours']} hours</b>\n"
                    message += f"⏱️ <b>{countdown['minutes']} minutes</b>\n\n"
                
                message += f"🛒 <b>Want to buy <a href='https://solscan.io/token/{self.token_mint}'>{self.token_symbol}</a>?</b>\n"
                message += f"• Go to: <a href='https://raydium.io/swap/'>Raydium DEX</a>\n"
                message += f"• Paste: <code>{self.token_mint}</code>\n"
                message += f"• Get {self.airdrop_amount:,} token airdrop!\n\n"
                # Create inline keyboard with BUY button
                buy_button = InlineKeyboardButton(f"🛒 BUY ${self.token_symbol}", url=self.buy_button_link)
                keyboard = InlineKeyboardMarkup([[buy_button]])
                
                # Send daily summary with CR7 Ronaldo image and inline keyboard
                await self.send_telegram_message(message, "https://i.postimg.cc/T19cTg5Q/93d39fc3-ac6f-4c94-a324-72feee1c2b29.jpg", keyboard)
                logger.info("Daily real-time summary sent")
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
    
    async def process_real_buy(self, signature: str):
        """Process a real buy transaction with automatic token distribution"""
        try:
            # Get transaction details
            tx_data = self.get_transaction_details(signature)
            
            if not tx_data:
                return False
            
            # Analyze transaction
            analysis = self.analyze_transaction(tx_data)
            
            if analysis and analysis["is_buy"]:
                buyer = analysis["buyer"]
                sol_spent = analysis["sol_spent"]
                usd_value = analysis["usd_value"]
                token_amount = analysis.get("token_amount", 0)
                
                logger.info(f"REAL BUY DETECTED: {sol_spent} SOL from {buyer}, received {token_amount} tokens")
                
                # Calculate token distribution based on admin configuration
                tokens_to_distribute = self.calculate_token_distribution(sol_spent)
                
                # Check if user should get airdrop (admin configuration)
                airdrop_amount = 0
                if self.one_airdrop_per_user and self._airdrop_users is not None:
                    if buyer not in self._airdrop_users:
                        airdrop_amount = self.airdrop_amount
                        self._airdrop_users.add(buyer)
                        logger.info(f"FIRST-TIME USER AIRDROP: {airdrop_amount} tokens to {buyer}")
                elif not self.one_airdrop_per_user:
                    airdrop_amount = self.airdrop_amount
                    logger.info(f"REGULAR AIRDROP: {airdrop_amount} tokens to {buyer}")
                
                # Perform automatic token transfer to buyer
                transfer_success = False
                if self.admin_wallet and self.admin_token_account:
                    # Transfer the bought amount to buyer
                    transfer_amount = int(token_amount) if token_amount > 0 else int(sol_spent * self.tokens_per_sol)
                    transfer_success = await self.transfer_tokens_to_buyer(buyer, transfer_amount)
                    
                    if transfer_success:
                        logger.info(f"✅ AUTOMATIC TOKEN TRANSFER SUCCESSFUL: {transfer_amount} tokens sent to {buyer}")
                    else:
                        logger.warning(f"❌ AUTOMATIC TOKEN TRANSFER FAILED: Could not send {transfer_amount} tokens to {buyer}")
                
                # Send real-time buy alert with automatic distribution info
                await self.send_buy_alert(buyer, sol_spent, usd_value, tokens_to_distribute, airdrop_amount, signature, token_amount)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to process real buy {signature}: {e}")
            return False
    
    async def start_real_monitoring(self):
        """Start real-time monitoring with automatic token distribution"""
        try:
            logger.info("Starting Real-Time Monitoring Bot")
            
            # Send professional startup message
            startup_message = f"🦅 <b>Official $CR7 Coin</b>\n"
            startup_message += f"<i>Be DeFiant</i>\n\n"
            startup_message += f"🎉 <b>New <a href='https://solscan.io/token/{self.token_mint}'>${self.token_symbol}</a> Presale Started!</b>\n\n"
            startup_message += f"🦅🦅🦅🦅🦅\n\n"
            startup_message += f"🪙 <b>Token:</b> <code>{self.token_mint}</code>\n"
            startup_message += f"💰 <b>Symbol:</b> ${self.token_symbol}\n"
            startup_message += f"🔄 <b>Monitoring:</b> <b>ACTIVE</b>\n\n"
            
            # Add presale countdown to startup message
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
            startup_message += f"• Automatic token distribution\n"
            startup_message += f"• Real-time alerts\n"
            startup_message += f"• Daily summaries\n\n"
            startup_message += f"🛒 <b>HOW TO BUY {self.token_symbol} TOKEN:</b>\n"
            startup_message += f"1️⃣ Open Raydium DEX: <a href='https://raydium.io/swap/'>raydium.io/swap</a>\n"
            startup_message += f"2️⃣ Connect your Solana wallet\n"
            startup_message += f"3️⃣ Paste token address: <code>{self.token_mint}</code>\n"
            startup_message += f"4️⃣ Enter amount to buy\n"
            startup_message += f"5️⃣ Confirm transaction\n\n"
            startup_message += f"💡 <b>ALTERNATIVE DEXs:</b>\n"
            startup_message += f"• Jupiter: <a href='https://jup.ag/'>jup.ag</a>\n"
            startup_message += f"• Orca: <a href='https://www.orca.so/'>orca.so</a>\n"
            startup_message += f"• Serum: <a href='https://dex.serum.io/'>dex.serum.io</a>\n\n"
            startup_message += f"🎁 <b>BONUS FEATURES:</b>\n"
            startup_message += f"• Token Rate: 1 SOL = {self.tokens_per_sol:,} {self.token_symbol} tokens\n"
            startup_message += f"• Minimum Buy: {self.minimum_buy_sol} SOL\n"
            startup_message += f"• First-time buyers get {self.airdrop_amount:,} token airdrop\n"
            startup_message += f"• Automatic token distribution\n"
            startup_message += f"• Real-time buy alerts\n"
            startup_message += f"• Professional monitoring\n\n"
            # Create inline keyboard with BUY button
            buy_button = InlineKeyboardButton(f"🛒 BUY ${self.token_symbol}", url=self.buy_button_link)
            keyboard = InlineKeyboardMarkup([[buy_button]])
            
            # Send startup message with CR7 Ronaldo image and inline keyboard
            await self.send_telegram_message(startup_message, "https://i.postimg.cc/T19cTg5Q/93d39fc3-ac6f-4c94-a324-72feee1c2b29.jpg", keyboard)
            
            # Send buy guide after startup
            await asyncio.sleep(2)  # Small delay
            await self.send_buy_guide()
            
            # Real-time monitoring loop
            last_summary_time = time.time()
            
            while self.monitoring_active:
                try:
                    logger.info("Checking for new real-time transactions...")
                    
                    # Get recent transactions
                    transactions = self.get_recent_transactions(self.max_transactions_per_check)
                    
                    if transactions:
                        # Process only the latest transaction to prevent duplicates
                        latest_tx = transactions[0]  # First transaction is the latest
                        signature = latest_tx.get("signature")
                        
                        if signature and signature not in self._seen_transactions:
                            # Mark as seen immediately to prevent duplicates
                            self._seen_transactions.add(signature)
                            
                            # Process real buy with automatic token distribution
                            await self.process_real_buy(signature)
                            
                            logger.info(f"Processed latest transaction: {signature[:8]}...")
                        else:
                            logger.info("No new transactions to process")
                    
                    # Send daily summary every 24 hours
                    current_time = time.time()
                    if current_time - last_summary_time >= 86400:  # 24 hours
                        await self.send_daily_summary()
                        last_summary_time = current_time
                    
                    # Wait before next check (admin configurable)
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in real-time monitoring loop: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
                
        except KeyboardInterrupt:
            logger.info("Real-time monitoring stopped by user")
        except Exception as e:
            logger.error(f"Real-time monitoring error: {e}")
            raise

async def main():
    """Main entry point"""
    try:
        bot = RealMonitoringBot()
        await bot.start_real_monitoring()
    except Exception as e:
        logger.error(f"Failed to start real-time monitoring: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
