#!/usr/bin/env python3
"""
CR7 Token Bot - Interactive Configuration Setup Script
This script helps you configure the config.json file step by step.
"""

import json
import os
import sys
from dotenv import load_dotenv

def print_header():
    """Print welcome header"""
    print("=" * 60)
    print("🚀 CR7 Token Bot - Configuration Setup")
    print("=" * 60)
    print("This script will help you configure your config.json file.")
    print("Make sure you have all the required information ready.")
    print("=" * 60)

def get_input(prompt, required=True, default=None):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print("❌ This field is required. Please enter a value.")
            continue
        
        return user_input

def get_telegram_bot_token():
    """Get Telegram bot token"""
    print("\n📱 TELEGRAM BOT TOKEN")
    print("-" * 30)
    print("1. Go to Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Choose a name for your bot")
    print("4. Choose a username (must end with 'bot')")
    print("5. Copy the token provided")
    print()
    
    token = get_input("Enter your Telegram bot token")
    
    # Basic validation
    if not token.count(':') == 1:
        print("❌ Invalid token format. Should be like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        return get_telegram_bot_token()
    
    return token

def get_telegram_group_id():
    """Get Telegram group ID"""
    print("\n👥 TELEGRAM GROUP ID")
    print("-" * 30)
    print("1. Add your bot to your Telegram group")
    print("2. Send a message in the group")
    print("3. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("4. Find your group ID in the response (starts with -100)")
    print()
    
    group_id = get_input("Enter your Telegram group ID")
    
    # Basic validation
    if not group_id.startswith('-100'):
        print("❌ Invalid group ID format. Should start with -100")
        return get_telegram_group_id()
    
    return group_id

def get_solana_rpc():
    """Get Solana RPC URL"""
    print("\n🔗 SOLANA RPC URL")
    print("-" * 30)
    print("Choose an RPC provider:")
    print("1. Free (rate limited): https://api.mainnet-beta.solana.com")
    print("2. Alchemy (paid, recommended): https://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY")
    print("3. Ankr (free): https://rpc.ankr.com/solana")
    print("4. Custom")
    print()
    
    choice = get_input("Choose option (1-4)", default="1")
    
    if choice == "1":
        return "https://api.mainnet-beta.solana.com"
    elif choice == "2":
        api_key = get_input("Enter your Alchemy API key")
        return f"https://solana-mainnet.g.alchemy.com/v2/{api_key}"
    elif choice == "3":
        return "https://rpc.ankr.com/solana"
    else:
        return get_input("Enter your custom RPC URL")

def get_token_mint():
    """Get token mint address"""
    print("\n🪙 TOKEN MINT ADDRESS")
    print("-" * 30)
    print("This is your CR7 token's unique address on Solana.")
    print("You can find it on Solscan or your token creation transaction.")
    print()
    
    mint = get_input("Enter your CR7 token mint address")
    
    # Basic validation
    if len(mint) < 32:
        print("❌ Invalid mint address format. Should be a long string.")
        return get_token_mint()
    
    return mint

def get_wallet_private_key():
    """Get wallet private key"""
    print("\n🔐 WALLET PRIVATE KEY")
    print("-" * 30)
    print("⚠️  SECURITY WARNING: This will be stored in config.json")
    print("Make sure to use a dedicated wallet for the bot only!")
    print()
    print("How to get your private key:")
    print("1. Phantom Wallet: Settings → Export Private Key")
    print("2. Solflare Wallet: Settings → Export Private Key")
    print("3. Enter your password when prompted")
    print()
    
    private_key = get_input("Enter your private key (long string)")
    
    # Convert to array format
    try:
        private_key_array = [ord(char) for char in private_key]
        return private_key_array
    except Exception as e:
        print(f"❌ Error converting private key: {e}")
        return get_wallet_private_key()

def get_buy_button_link(token_mint):
    """Get buy button link"""
    print("\n🛒 BUY BUTTON LINK")
    print("-" * 30)
    print("Choose a DEX for your buy button:")
    print("1. Raydium (recommended)")
    print("2. Jupiter")
    print("3. Orca")
    print("4. Custom")
    print()
    
    choice = get_input("Choose option (1-4)", default="1")
    
    if choice == "1":
        return f"https://raydium.io/swap/?inputMint=sol&outputMint={token_mint}"
    elif choice == "2":
        return f"https://jup.ag/swap/SOL-{token_mint}"
    elif choice == "3":
        return f"https://www.orca.so/swap?inputMint=sol&outputMint={token_mint}"
    else:
        return get_input("Enter your custom buy button link")

def get_presale_settings():
    """Get presale settings"""
    print("\n⏰ PRESALE SETTINGS")
    print("-" * 30)
    
    end_date = get_input("Enter presale end date (YYYY-MM-DD HH:MM:SS)", default="2025-09-06 23:59:59")
    timezone = get_input("Enter timezone", default="UTC")
    
    return end_date, timezone

def get_distribution_settings():
    """Get distribution settings"""
    print("\n🎁 DISTRIBUTION SETTINGS")
    print("-" * 30)
    
    ratio = float(get_input("Distribution ratio (1.0 = 100%)", default="1.0"))
    tokens_per_sol = int(get_input("Tokens per SOL (1 SOL = ? tokens)", default="7000"))
    min_buy_sol = float(get_input("Minimum buy amount in SOL", default="0.2"))
    min_dist = int(get_input("Minimum distribution amount", default="1400"))
    max_dist = int(get_input("Maximum distribution amount", default="1000000"))
    airdrop = int(get_input("Airdrop amount for new users", default="1000"))
    
    return ratio, tokens_per_sol, min_buy_sol, min_dist, max_dist, airdrop

def get_monitoring_settings():
    """Get monitoring settings"""
    print("\n⚙️ MONITORING SETTINGS")
    print("-" * 30)
    
    interval = int(get_input("Check interval in seconds", default="3"))
    max_tx = int(get_input("Maximum transactions per check", default="10"))
    delay = int(get_input("Rate limit delay in seconds", default="1"))
    
    return interval, max_tx, delay

def create_env_file(config):
    """Create .env file for sensitive information"""
    try:
        env_content = f"""# CR7 Token Bot - Environment Variables
# Keep this file secure and never share it publicly

# Telegram Configuration
TELEGRAM_BOT_TOKEN={config['TELEGRAM_BOT_TOKEN']}
TELEGRAM_GROUP_ID={config['TELEGRAM_GROUP_ID']}

# Solana Configuration
SOLANA_RPC={config['SOLANA_RPC']}
TOKEN_MINT={config['TOKEN_MINT']}

# Wallet Configuration (PRIVATE KEY - KEEP SECURE!)
WALLET_PRIVATE_KEY={','.join(map(str, config['WALLET_PRIVATE_KEY']))}

# Token Distribution Settings
TOKENS_PER_SOL={config['TOKENS_PER_SOL']}
MINIMUM_BUY_SOL={config['MINIMUM_BUY_SOL']}
DISTRIBUTION_RATIO={config['DISTRIBUTION_RATIO']}
MIN_DISTRIBUTION={config['MIN_DISTRIBUTION']}
MAX_DISTRIBUTION={config['MAX_DISTRIBUTION']}
AIRDROP_AMOUNT={config['AIRDROP_AMOUNT']}

# Buy Button and Presale
BUY_BUTTON_LINK={config['BUY_BUTTON_LINK']}
PRESALE_END_DATE={config['PRESALE_END_DATE']}
PRESALE_TIMEZONE={config['PRESALE_TIMEZONE']}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print("⚠️  IMPORTANT: Keep .env file secure and never share it publicly!")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def create_config():
    """Create configuration file"""
    print_header()
    
    # Get all configuration values
    bot_token = get_telegram_bot_token()
    group_id = get_telegram_group_id()
    rpc_url = get_solana_rpc()
    token_mint = get_token_mint()
    private_key = get_wallet_private_key()
    buy_link = get_buy_button_link(token_mint)
    presale_date, presale_timezone = get_presale_settings()
    ratio, tokens_per_sol, min_buy_sol, min_dist, max_dist, airdrop = get_distribution_settings()
    interval, max_tx, delay = get_monitoring_settings()
    
    # Create config dictionary
    config = {
        "TELEGRAM_BOT_TOKEN": bot_token,
        "TELEGRAM_GROUP_ID": group_id,
        "SOLANA_RPC": rpc_url,
        "TOKEN_MINT": token_mint,
        "TOKEN_SYMBOL": "CR7",
        "CHECK_INTERVAL": interval,
        "MAX_TRANSACTIONS_PER_CHECK": max_tx,
        "RATE_LIMIT_DELAY": delay,
        "DISTRIBUTION_RATIO": ratio,
        "TOKENS_PER_SOL": tokens_per_sol,
        "MINIMUM_BUY_SOL": min_buy_sol,
        "MIN_DISTRIBUTION": min_dist,
        "MAX_DISTRIBUTION": max_dist,
        "AIRDROP_AMOUNT": airdrop,
        "ALLOW_ONE_AIRDROP_PER_USER": True,
        "WALLET_PRIVATE_KEY": private_key,
        "BUY_BUTTON_LINK": buy_link,
        "PRESALE_END_DATE": presale_date,
        "PRESALE_TIMEZONE": presale_timezone
    }
    
    # Save to files
    try:
        # Save config.json
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create .env file for sensitive information
        create_env_file(config)
        
        print("\n" + "=" * 60)
        print("✅ Configuration saved successfully!")
        print("=" * 60)
        print("Your config.json file has been created.")
        print("Your .env file has been created for sensitive information.")
        print("You can now start your bot with: python main.py")
        print("=" * 60)
        print("⚠️  SECURITY REMINDER:")
        print("• Keep .env file secure and never share it publicly")
        print("• Add .env to .gitignore if using version control")
        print("• The bot will use .env values over config.json values")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        sys.exit(1)

def main():
    """Main function"""
    if os.path.exists('config.json'):
        print("⚠️  config.json already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Configuration cancelled.")
            sys.exit(0)
    
    create_config()

if __name__ == "__main__":
    main()
