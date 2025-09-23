# Toka 420 TimeBot — v4 Modular Scaffold

🌿⛵ **Weedcoin ritual bot** built as a personal learning project.  
This bot posts ritual 4:20 messages across global market hubs, pulling live price anchors from Dexscreener and weaving them into cultural rhythm.

---

## Features
- Modular design (each service can be swapped or removed without breaking the bot)
- Telegram commands:
  - `/status` → check if the bot is alive
  - `/id` → return your chat ID
  - `/token <symbol>` → fetch price anchor for a token (24h % | price | volume)
  - `/news` → pull one crypto news headline
- Fail-open behavior (if a module fails, the bot keeps running)
- Simple JSON logging for state and prices

---

## Setup
1. Clone this repo  
2. Install dependencies  
3. Copy `.env.example` to `.env` and add your TELEGRAM_TOKEN  
4. Run: `python app.py`

---

✨ *Keep your canoe balanced. Bongterm > FOMO.*
