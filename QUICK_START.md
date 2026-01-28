# QUICK START GUIDE - What You Need To Do Manually

## Step 1: Install Python & Dependencies ✓ READY

Your project structure is complete. Now you need to:

```bash
# Navigate to project directory
cd d:\Github Projects\grafenberg_langpen_binance_bot

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get Binance Testnet API Keys ⚠️ YOU MUST DO THIS

### Create Binance Testnet Account
1. Go to **https://testnet.binancefuture.com**
2. Click "Sign up" 
3. Create account (email + password, no KYC needed)

### Generate API Keys
1. Login to Binance Testnet
2. Click on your profile → API Management
3. Create New Key
4. Name it: "TradingBot"
5. Copy both:
   - **API Key** (public)
   - **Secret Key** (keep it private!)

## Step 3: Configure Environment ⚠️ YOU MUST DO THIS

1. Open `.env` file in project root
2. Replace these lines with your actual credentials:

```
BINANCE_API_KEY=paste_your_api_key_here
BINANCE_SECRET_KEY=paste_your_secret_key_here
ENVIRONMENT=testnet
```

**Example:**
```
BINANCE_API_KEY=1a2b3c4d5e6f7g8h9i0j
BINANCE_SECRET_KEY=abcdefghijklmnopqrstuvwxyz123456
ENVIRONMENT=testnet
```

⚠️ **IMPORTANT**: Never share or commit `.env` file to GitHub

## Step 4: Test The Bot

```bash
# Verify installation works
python bot.py --help

# You should see all available commands

# Try a simple market order (will fail if API not configured)
python bot.py market --symbol BTCUSDT --side BUY --quantity 0.001
```

## Step 5: Check Logs

Every action is logged to `logs/bot.log`

```bash
# View logs (Windows PowerShell)
Get-Content logs/bot.log -Tail 20

# Or with cmd
type logs/bot.log
```

## Available Commands After Setup

### Market Orders
```bash
python bot.py market --symbol BTCUSDT --side BUY --quantity 0.01
python bot.py market --symbol ETHUSDT --side SELL --quantity 0.1
```

### Limit Orders
```bash
python bot.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 40000
```

### Advanced Orders
```bash
# Stop-Limit
python bot.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.01 --stop 38000 --limit 37500

# OCO (Take Profit + Stop Loss)
python bot.py oco --symbol BTCUSDT --side BUY --quantity 0.01 --take-profit 42000 --stop-loss 38000

# TWAP (Split order over time)
python bot.py twap --symbol BTCUSDT --side BUY --quantity 1.0 --orders 5 --interval 60

# Grid Trading
python bot.py grid --symbol BTCUSDT --lower 40000 --upper 42000 --grids 10 --investment 1000
```

## Common Issues

### "ModuleNotFoundError: No module named 'binance'"
- You haven't activated venv or installed requirements
- Run: `pip install -r requirements.txt`

### "Missing API credentials"
- Your `.env` file is missing or empty
- Create `.env` and add your Testnet API keys

### "Invalid symbol BTCUSDT"
- Make sure you have funds in Testnet account
- Visit https://testnet.binancefuture.com and check account

### "Insufficient balance"
- Testnet account has no default balance
- You need to request test funds on Binance Testnet

## File Structure (What's Already Created)

```
d:\Github Projects\grafenberg_langpen_binance_bot\
├── src/
│   ├── __init__.py              ✓ Created
│   ├── config.py                ✓ Created (Configuration)
│   ├── logger.py                ✓ Created (Logging system)
│   ├── validators.py            ✓ Created (Input validation)
│   ├── api_client.py            ✓ Created (API wrapper)
│   ├── market_orders.py         ✓ Created (Market orders)
│   ├── limit_orders.py          ✓ Created (Limit orders)
│   ├── performance_tracker.py   ✓ Created (Metrics)
│   └── advanced/
│       ├── __init__.py          ✓ Created
│       ├── stop_limit.py        ✓ Created
│       ├── oco.py               ✓ Created
│       ├── twap.py              ✓ Created
│       └── grid.py              ✓ Created
├── logs/                        ✓ Created (will have logs)
├── tests/                       ✓ Created (ready for tests)
├── bot.py                       ✓ Created (Main CLI)
├── requirements.txt             ✓ Created
├── .env.example                 ✓ Created (COPY & EDIT THIS)
├── .env                         ⚠️ YOU CREATE (from .env.example)
├── .gitignore                   ✓ Created
└── README.md                    ✓ Created (Full documentation)
```

## Next Steps

1. **Do Step 1-3 above** (Install, get API keys, configure)
2. Run test command: `python bot.py --help`
3. Try a small market order to verify
4. Check logs: `Get-Content logs/bot.log -Tail 10`
5. Start using advanced strategies

## Key Features You Have Access To

✓ **Core Orders**: Market, Limit  
✓ **Advanced Orders**: Stop-Limit, OCO, TWAP, Grid  
✓ **Validation**: Comprehensive input checking  
✓ **Logging**: Structured, timestamped, rotating logs  
✓ **Risk Management**: Balance checks, leverage control  
✓ **Performance Tracking**: P&L, win rate, metrics  

---

**Need Help?**
- Read `README.md` for full documentation
- Check `logs/bot.log` for error details
- Review `.env.example` for configuration template
