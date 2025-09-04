# 🚀 CR7 Token Bot - Complete Configuration Guide

## 📋 **Table of Contents**
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration File Setup](#configuration-file-setup)
4. [Step-by-Step Configuration](#step-by-step-configuration)
5. [Advanced Settings](#advanced-settings)
6. [Security Best Practices](#security-best-practices)
7. [Testing Your Configuration](#testing-your-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)

---

## 🎯 **Overview**

This guide will help you configure the `config.json` file for your CR7 Token Bot to monitor real-time token transactions and send automatic alerts to your Telegram group.

**What the bot does:**
- ✅ Monitors Solana blockchain for CR7 token transactions
- ✅ Sends real-time buy alerts to your Telegram group
- ✅ Automatically distributes tokens to buyers
- ✅ Sends airdrops to first-time buyers
- ✅ Displays professional messages with branding

---

## 🔧 **Prerequisites**

Before configuring the bot, you need:

1. **Telegram Bot Token** - Create a bot via @BotFather
2. **Telegram Group ID** - Your group where alerts will be sent
3. **Solana RPC URL** - For blockchain monitoring
4. **Token Mint Address** - Your CR7 token address
5. **Admin Wallet Private Key** - For token distribution
6. **Buy Button Link** - DEX link for token purchases

---

## 📁 **Configuration File Setup**

### **File Location:**
```
CR7_Token_Bot_Delivery/
├── config.json          ← Non-sensitive configuration file
├── .env                 ← Sensitive information (private keys, tokens)
├── env_template.txt     ← Template for .env file
├── main.py
├── requirements.txt
└── README.md
```

### **File Structure:**
- **`config.json`**: Contains non-sensitive settings (intervals, limits, etc.)
- **`.env`**: Contains sensitive information (private keys, bot tokens, etc.)
- **`env_template.txt`**: Template file for creating your own .env file

---

## ⚙️ **Step-by-Step Configuration**

### **Step 0: Environment Variables Setup**

**For Security, we use two configuration files:**

1. **Create `.env` file** (for sensitive information):
```bash
# Copy the template
cp env_template.txt .env

# Edit .env file with your sensitive information
```

2. **Example `.env` file:**
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_GROUP_ID=your_group_id_here

# Solana Configuration
SOLANA_RPC=https://api.mainnet-beta.solana.com
TOKEN_MINT=your_token_mint_here

# Wallet Configuration (PRIVATE KEY - KEEP SECURE!)
WALLET_PRIVATE_KEY=12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78,90,12,34,56,78

# Token Distribution Settings
TOKENS_PER_SOL=7000
MINIMUM_BUY_SOL=0.2
DISTRIBUTION_RATIO=1.0
MIN_DISTRIBUTION=1400
MAX_DISTRIBUTION=1000000
AIRDROP_AMOUNT=1000

# Buy Button and Presale
BUY_BUTTON_LINK=https://raydium.io/swap/?inputMint=sol&outputMint=YOUR_TOKEN_MINT
PRESALE_END_DATE=2025-09-06 23:59:59
PRESALE_TIMEZONE=UTC
```

### **Step 1: Basic Bot Settings**

```json
{
  "TELEGRAM_BOT_TOKEN": "YOUR_BOT_TOKEN_HERE",
  "TELEGRAM_GROUP_ID": "YOUR_GROUP_ID_HERE"
}
```

**How to get these values:**

#### **Telegram Bot Token:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "CR7 Token Monitor")
4. Choose a username (e.g., "cr7_token_monitor_bot")
5. Copy the token provided (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### **Telegram Group ID:**
1. Add your bot to your Telegram group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your group ID in the response (format: `-1001234567890`)

### **Step 2: Solana Blockchain Settings**

```json
{
  "SOLANA_RPC_URL": "https://api.mainnet-beta.solana.com",
  "TOKEN_MINT": "9FwBttHVkmTGECS8oveN26RTQYS4pjbyKf4K3C1jJZ7o"
}
```

**RPC URL Options:**
- **Free:** `https://api.mainnet-beta.solana.com` (rate limited)
- **Paid (Recommended):** `https://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY`
- **Alternative:** `https://rpc.ankr.com/solana`

**Token Mint Address:**
- This is your CR7 token's unique address on Solana
- Replace with your actual token mint address

### **Step 3: Monitoring Settings**

```json
{
  "CHECK_INTERVAL": 3,
  "MAX_TRANSACTIONS": 10,
  "RATE_LIMIT_DELAY": 1
}
```

**Explanation:**
- **CHECK_INTERVAL:** How often to check for new transactions (seconds)
- **MAX_TRANSACTIONS:** Maximum transactions to fetch per check
- **RATE_LIMIT_DELAY:** Delay between API calls to avoid rate limits

### **Step 4: Token Distribution Settings**

```json
{
  "DISTRIBUTION_RATIO": 1.0,
  "TOKENS_PER_SOL": 7000,
  "MINIMUM_BUY_SOL": 0.2,
  "MIN_DISTRIBUTION": 1400,
  "MAX_DISTRIBUTION": 1000000,
  "AIRDROP_AMOUNT": 1000,
  "ALLOW_ONE_AIRDROP_PER_USER": true
}
```

**Explanation:**
- **DISTRIBUTION_RATIO:** Percentage of bought tokens to distribute (1.0 = 100%)
- **TOKENS_PER_SOL:** Token rate - 1 SOL = 7000 CR7 tokens
- **MINIMUM_BUY_SOL:** Minimum SOL amount required for a buy (0.2 SOL)
- **MIN_DISTRIBUTION:** Minimum tokens to distribute (1400 = 0.2 SOL × 7000)
- **MAX_DISTRIBUTION:** Maximum tokens to distribute
- **AIRDROP_AMOUNT:** Free tokens for first-time buyers
- **ALLOW_ONE_AIRDROP_PER_USER:** Whether to send airdrop only once per user

### **Step 5: Wallet Configuration**

```json
{
  "WALLET_PRIVATE_KEY": [123, 45, 67, 89, ...]
}
```

**⚠️ CRITICAL SECURITY STEP:**

#### **How to get your private key:**
1. **From Phantom Wallet:**
   - Open Phantom wallet
   - Go to Settings → Export Private Key
   - Enter your password
   - Copy the private key

2. **From Solflare Wallet:**
   - Open Solflare wallet
   - Go to Settings → Export Private Key
   - Copy the private key

3. **Convert to Array Format:**
   - Your private key will be a long string
   - Use an online converter or Python script to convert to array format
   - Example: `"abc123..."` → `[97, 98, 99, 49, 50, 51, ...]`

#### **Python Script to Convert Private Key:**
```python
# Convert private key string to array
private_key_string = "YOUR_PRIVATE_KEY_HERE"
private_key_array = [ord(char) for char in private_key_string]
print(private_key_array)
```

### **Step 6: Buy Button and Presale Settings**

```json
{
  "BUY_BUTTON_LINK": "https://raydium.io/swap/?inputMint=sol&outputMint=YOUR_TOKEN_MINT",
  "PRESALE_END_DATE": "2025-09-06 23:59:59",
  "PRESALE_TIMEZONE": "UTC"
}
```

**Buy Button Link:**
- Replace `YOUR_TOKEN_MINT` with your actual token mint address
- Popular DEX options:
  - Raydium: `https://raydium.io/swap/?inputMint=sol&outputMint=YOUR_TOKEN_MINT`
  - Jupiter: `https://jup.ag/swap/SOL-YOUR_TOKEN_MINT`
  - Orca: `https://www.orca.so/swap?inputMint=sol&outputMint=YOUR_TOKEN_MINT`

**Presale Settings:**
- **PRESALE_END_DATE:** When your presale ends (YYYY-MM-DD HH:MM:SS)
- **PRESALE_TIMEZONE:** Timezone for the end date (UTC, EST, PST, etc.)

---

## 🔒 **Security Best Practices**

### **1. Private Key Security**
- ✅ **Never share your private key**
- ✅ **Use a dedicated wallet for the bot**
- ✅ **Keep only necessary tokens in the bot wallet**
- ✅ **Regularly monitor wallet activity**

### **2. Bot Token Security**
- ✅ **Don't share your Telegram bot token**
- ✅ **Use environment variables in production**
- ✅ **Regularly rotate tokens if compromised**

### **3. Group Security**
- ✅ **Make your group private**
- ✅ **Add trusted admins only**
- ✅ **Monitor bot permissions**

---

## 🧪 **Testing Your Configuration**

### **Step 1: Validate JSON Format**
```bash
# Check if config.json is valid
python -c "import json; json.load(open('config.json')); print('✅ Valid JSON')"
```

### **Step 2: Test Bot Connection**
```python
# Test script to verify configuration
import json
from telegram import Bot

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Test Telegram connection
bot = Bot(token=config['TELEGRAM_BOT_TOKEN'])
print("✅ Bot token is valid")

# Test group access
try:
    updates = bot.get_updates()
    print("✅ Bot can access Telegram API")
except Exception as e:
    print(f"❌ Error: {e}")
```

### **Step 3: Test Solana Connection**
```python
# Test Solana RPC connection
import requests

rpc_url = config['SOLANA_RPC_URL']
response = requests.post(rpc_url, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getHealth"
})

if response.status_code == 200:
    print("✅ Solana RPC is working")
else:
    print("❌ Solana RPC connection failed")
```

---

## 🚀 **Complete Configuration Example**

Here's a complete `config.json` example:

```json
{
  "TELEGRAM_BOT_TOKEN": "7570326283:AAE1Eg_zDJTVy8og1mRq7ADlGUVjCoXtSgY",
  "TELEGRAM_GROUP_ID": "@testgroupbd420",
  "SOLANA_RPC": "https://api.mainnet-beta.solana.com",
  "TOKEN_MINT": "9FwBttHVkmTGECS8oveN26RTQYS4pjbyKf4K3C1jJZ7o",
  "TOKEN_SYMBOL": "CR7",
  "CHECK_INTERVAL": 60,
  "MAX_TRANSACTIONS_PER_CHECK": 20,
  "RATE_LIMIT_DELAY": 2,
  "DISTRIBUTION_RATIO": 1.0,
  "TOKENS_PER_SOL": 7000,
  "MINIMUM_BUY_SOL": 0.2,
  "MIN_DISTRIBUTION": 1400,
  "MAX_DISTRIBUTION": 1000000,
  "AIRDROP_AMOUNT": 1000,
  "ALLOW_ONE_AIRDROP_PER_USER": true,
  "WALLET_PRIVATE_KEY": [123, 45, 67, 89, 101, 112, 131, 145, 159, 163, 177, 191, 205, 219, 233, 247, 261, 275, 289, 303, 317, 331, 345, 359, 373, 387, 401, 415, 429, 443, 457, 471, 485, 499, 513, 527, 541, 555, 569, 583, 597, 611, 625, 639, 653, 667, 681, 695, 709, 723, 737, 751, 765, 779, 793, 807, 821, 835, 849, 863, 877, 891, 905, 919],
  "BUY_BUTTON_LINK": "https://raydium.io/swap/?inputMint=sol&outputMint=9FwBttHVkmTGECS8oveN26RTQYS4pjbyKf4K3C1jJZ7o",
  "PRESALE_END_DATE": "2025-09-06 23:59:59",
  "PRESALE_TIMEZONE": "UTC"
}
```

---

## 🔧 **Troubleshooting**

### **Common Issues and Solutions:**

#### **1. "Invalid Bot Token" Error**
- ✅ Check if bot token is correct
- ✅ Ensure bot is added to your group
- ✅ Verify bot has admin permissions

#### **2. "Group ID Not Found" Error**
- ✅ Check group ID format (should start with -100)
- ✅ Ensure bot is added to the group
- ✅ Send a message in the group first

#### **3. "Solana RPC Error"**
- ✅ Check RPC URL is correct
- ✅ Try a different RPC endpoint
- ✅ Check if you're hitting rate limits

#### **4. "Private Key Error"**
- ✅ Ensure private key is in array format
- ✅ Check if wallet has sufficient SOL for transactions
- ✅ Verify wallet has the token for distribution

#### **5. "Token Distribution Failed"**
- ✅ Check if admin wallet has enough tokens
- ✅ Verify token mint address is correct
- ✅ Ensure wallet has SOL for transaction fees

---

## 🚀 **Production Deployment**

### **Step 1: Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Test configuration
python -c "import json; json.load(open('config.json'))"
```

### **Step 2: Run the Bot**
```bash
# Start the bot
python real_monitoring_bot.py
```

### **Step 3: Monitor Logs**
- Check console output for errors
- Monitor Telegram group for alerts
- Verify token distributions are working

### **Step 4: Production Tips**
- ✅ Use a VPS or cloud server for 24/7 operation
- ✅ Set up log rotation for large log files
- ✅ Monitor wallet balance regularly
- ✅ Keep backups of your configuration
- ✅ Update bot regularly for new features

---

## 📞 **Support**

If you encounter any issues:

1. **Check the logs** for error messages
2. **Verify your configuration** using the test scripts
3. **Test each component** individually
4. **Check network connectivity** to Solana and Telegram
5. **Ensure sufficient funds** in your admin wallet

---

## 🎯 **Quick Start Checklist**

- [ ] Telegram bot created and added to group
- [ ] Group ID obtained and verified
- [ ] Solana RPC URL configured
- [ ] Token mint address set
- [ ] Admin wallet private key configured
- [ ] Buy button link set
- [ ] Presale end date configured
- [ ] Configuration tested
- [ ] Bot started and monitoring

---

**🎉 Congratulations! Your CR7 Token Bot is now configured and ready for real-time monitoring!**

**Remember to keep your private keys secure and monitor your bot's performance regularly.**
