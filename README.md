# Toka 420 TimeBot

## Overview  
Toka 420 TimeBot is a modular Telegram + X relay bot.  
It announces **cryptocurrency market hub prerolls (4:00)** in Telegram and **Holy Minute posts (4:20)** in both Telegram and X.  
The bot is stateless, lean, and timezone-aware — focused on crypto markets and cannabis culture timing.

## Features  
- **Scheduler**:  
  - Preroll posts at **4:00 local time** in 15 global market hubs  
  - Holy Minute posts at **4:20 local time** in those hubs  
- **Relay**: 4:20 messages relayed to X (configurable on/off)  
- **Commands**:  
  - `/status` → last call, next scheduled call, news sources, X relay status  
  - `/news` → headlines filtered by region (time zone aware)  
  - `/token` → token snapshot (current price, 24h + 48h change, 24h volume)  
- **Stateless design**: no files, only in-memory timers & short-term caches  
- **Single log**: consistent INFO logging to `logs/bot.log`

## Structure
