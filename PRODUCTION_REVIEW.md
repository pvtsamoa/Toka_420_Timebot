# Production Readiness Review — Toka 420 Time Bot

**Date:** January 15, 2026  
**Status:** ⚠️ **REQUIRES FIXES** (7 critical issues, 8 warnings)

---

## Executive Summary

The bot has good foundational modularity and clean architecture, but has **critical gaps in logging, error handling, environment configuration, and deployment readiness** that must be addressed before production deployment.

**Risk Level:** 🔴 **HIGH** — Production deployment not recommended without fixes.

---

## 1. CODE QUALITY ✅ / ⚠️

### Strengths
- ✅ Modular design: Commands, services, and scheduler properly separated
- ✅ Clean imports and minimal duplication
- ✅ Functions are focused and have clear responsibilities
- ✅ Decent error recovery (fail-open behavior)

### Issues

#### 🔴 CRITICAL: Missing Logging Throughout
**Severity:** CRITICAL  
**Impact:** Cannot diagnose production issues

- **Problem:** Almost no logging in core modules
- **Files:** `app.py`, `scheduler.py`, `services/ritual_time.py`, `services/ritual.py`
- **Example:** `scheduler.py` silently loads hubs with no logging
- **Fix:** Add structured logging to all critical paths

```python
# BEFORE
def schedule_hubs(job_queue: JobQueue, callback):
    for hub in load_hubs():
        tz = pytz.timezone(hub["tz"])
        t420 = dt.time(hour=4, minute=20, tzinfo=tz)
        job_queue.run_daily(callback, time=t420, name=f"420_{hub['name']}")

# AFTER
logger = logging.getLogger(__name__)

def schedule_hubs(job_queue: JobQueue, callback):
    try:
        hubs = load_hubs()
        logger.info(f"Scheduling {len(hubs)} hubs")
        for hub in hubs:
            tz = pytz.timezone(hub["tz"])
            t420 = dt.time(hour=4, minute=20, tzinfo=tz)
            job_queue.run_daily(callback, time=t420, name=f"420_{hub['name']}")
            logger.debug(f"Scheduled {hub['name']} at {t420} ({hub['tz']})")
    except Exception as e:
        logger.exception(f"Failed to schedule hubs: {e}")
        raise
```

#### 🔴 CRITICAL: Bare Exception Handling
**Severity:** CRITICAL  
**Impact:** Silent failures, impossible debugging

- **Files:** `services/dexscreener.py`, `services/ritual.py`, `commands/news.py`, `commands/studies.py`
- **Problem:** Generic `except Exception: return None` masks real errors

```python
# BAD (multiple files)
except Exception:
    return None

# GOOD
except requests.Timeout:
    logger.warning(f"DexScreener timeout for {token_id}")
    return None
except requests.RequestException as e:
    logger.error(f"DexScreener request failed: {e}")
    return None
except Exception as e:
    logger.exception(f"Unexpected error in get_anchor: {e}")
    return None
```

#### 🟡 WARNING: Inconsistent Code Style
**Severity:** WARNING  
**Impact:** Reduced readability

- **Issue:** Mixed compact and expanded code (e.g., `dexscreener.py` has single-liners)
- **Example:** 
```python
# Dense (hard to read)
return sorted(pairs, key=lambda p: float(p.get("volume", {}).get("h24") or 0), reverse=True)[0]

# Better
highest_vol_pair = max(pairs, key=lambda p: float(p.get("volume", {}).get("h24") or 0))
return highest_vol_pair
```

#### 🟡 WARNING: No Type Hints in Some Modules
**Severity:** WARNING  
**Impact:** IDE support reduced, harder maintenance

- **Files:** `app.py`, `scheduler.py`, `services/ritual_time.py` missing type hints
- **Example:** Should be `def load_hubs() -> list[dict[str, str]]:`

---

## 2. SECURITY 🔴

### Issues

#### 🔴 CRITICAL: Exposed Secrets in `.env.example`
**Severity:** CRITICAL  
**Impact:** Accidental secret commits

- **Problem:** `.env.example` still has feature flags referencing removed features
- **Problem:** No `.env` in `.gitignore` documented

```dotenv
# Current .env.example (OUTDATED)
TELEGRAM_BOT_TOKEN=
TELEGRAM_SCOPE=all
FF_NEWS=1
FF_X_RELAY=0          # ← Feature flag for removed X relay
FF_PRE_ROLL=1         # ← Feature flag for removed preroll
CHAT_IDS=
WEEDCOIN_TOKEN=Weedcoin
```

**Fix:** Update `.env.example`

```dotenv
# Correct .env.example
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_GLOBAL_CHAT_ID=your_chat_id_here
TELEGRAM_SCOPE=all   # all|apac|emea|amer
WEEDCOIN_TOKEN=Weedcoin
DEFAULT_TOKEN=weedcoin
TZ=America/Los_Angeles
```

#### 🔴 CRITICAL: Missing Required Environment Variables
**Severity:** CRITICAL  
**Impact:** Bot crashes at runtime

- **Problem:** `TELEGRAM_GLOBAL_CHAT_ID` used but not documented or validated
- **Problem:** `ritual_time.py` calls `ritual_call()` which tries to send to this chat ID without checking

```python
# ritual_time.py - DANGEROUS
await context.bot.send_message(chat_id=os.getenv("TELEGRAM_GLOBAL_CHAT_ID"), text=text)
# If TELEGRAM_GLOBAL_CHAT_ID is None, this fails silently
```

**Fix:** Add validation on startup

```python
def validate_config():
    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_GLOBAL_CHAT_ID"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise ValueError(f"Missing required env vars: {missing}")
    logging.info("Config validation passed")

# In app.py main
if __name__ == "__main__":
    validate_config()
    build_app().run_polling(drop_pending_updates=True)
```

#### 🔴 CRITICAL: No Input Validation
**Severity:** CRITICAL  
**Impact:** Potential injection/crash attacks

- **Files:** `commands/token.py`, `commands/news.py`
- **Problem:** User input not sanitized

```python
# BEFORE - commands/token.py
async def token(update, context):
    if not context.args:
        cur = context.bot_data.get("token_override")
        await update.message.reply_text(f"Current token: {cur or 'DEFAULT'}"); return
    new = context.args[0].strip()  # ← No validation!
    context.bot_data["token_override"] = new
    await update.message.reply_text(f"✅ Token set for this run: {new}")

# AFTER
async def token(update, context):
    if not context.args:
        cur = context.bot_data.get("token_override")
        await update.message.reply_text(f"Current token: {cur or 'DEFAULT'}")
        return
    new = context.args[0].strip()
    if not new or len(new) > 100 or not new.isalnum():  # Validate
        await update.message.reply_text("❌ Invalid token. Use alphanumeric, max 100 chars.")
        return
    context.bot_data["token_override"] = new
    await update.message.reply_text(f"✅ Token set: {new}")
```

#### 🟡 WARNING: No Rate Limiting
**Severity:** WARNING  
**Impact:** DOS vulnerability, API quota exhaustion

- **Problem:** Commands can be spammed without limits
- **Impact:** Could exhaust DexScreener API quota or overwhelm Telegram

**Fix:** Add command cooldowns (use `python-telegram-bot`'s built-in mechanisms or custom decorator)

#### 🟡 WARNING: Hardcoded Feed URLs
**Severity:** WARNING  
**Impact:** No flexibility for URL changes, credentials embedded in code

- **Files:** `commands/news.py`, `commands/studies.py`
- **Consider:** Moving to JSON config file

---

## 3. LOGGING & ERROR HANDLING 🔴

### Issues

#### 🔴 CRITICAL: Missing Startup Logging
**Severity:** CRITICAL  
**Impact:** Cannot diagnose startup failures

```python
# app.py - BEFORE
if __name__ == "__main__":
    build_app().run_polling(drop_pending_updates=True)

# app.py - AFTER
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/bot.log")
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting Toka 420 Time Bot v1")
        app = build_app()
        logger.info("Bot initialized successfully")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise
```

#### 🔴 CRITICAL: No Structured Error Context
**Severity:** CRITICAL  
**Impact:** Cannot correlate errors to users/chats

```python
# error_handler.py - BEFORE
async def on_error(update, context):
    if isinstance(context.error, NetworkError):
        logging.warning("Network glitch during polling: %s", context.error)
        return
    logging.exception("Unhandled error: %s", context.error)

# error_handler.py - AFTER
async def on_error(update, context):
    logger = logging.getLogger(__name__)
    
    # Include context
    chat_id = update.effective_chat.id if update else "unknown"
    user_id = update.effective_user.id if update else "unknown"
    
    if isinstance(context.error, NetworkError):
        logger.warning(
            f"Network error | chat={chat_id} user={user_id}",
            exc_info=context.error
        )
        return
    
    logger.exception(
        f"Unhandled error | chat={chat_id} user={user_id}",
        exc_info=context.error
    )
    
    # Notify user of error
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ An error occurred. Our team has been notified."
        )
    except Exception as notify_error:
        logger.exception(f"Failed to notify user: {notify_error}")
```

#### 🟡 WARNING: No Job Execution Logging
**Severity:** WARNING  
**Impact:** Cannot track if rituals actually executed

```python
# services/ritual_time.py - ADD
async def ritual_call(context):
    logger = logging.getLogger(__name__)
    hub_name = context.job.name.replace("420_", "")
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "weedcoin")
    
    try:
        logger.info(f"🌊 Ritual starting for {hub_name} with token={token}")
        text = build_ritual_text(hub_name, token)
        chat_id = os.getenv("TELEGRAM_GLOBAL_CHAT_ID")
        
        if not chat_id:
            logger.error(f"❌ TELEGRAM_GLOBAL_CHAT_ID not set!")
            return
        
        await context.bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"✅ Ritual sent for {hub_name}")
    except Exception as e:
        logger.exception(f"❌ Ritual failed for {hub_name}: {e}")
```

---

## 4. SCALABILITY & PERFORMANCE 🟡

### Issues

#### 🟡 WARNING: Global Cache Without TTL Management
**Severity:** WARNING  
**Impact:** Memory leak potential, stale data

```python
# services/dexscreener.py - CURRENT
_cache = {"key": None, "data": None, "ts": 0, "ttl": 60}

# ISSUE: Only one cached token at a time. Better approach:
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def get_anchor_cached(token_id: str):
    # LRU handles eviction automatically
    return _fetch_anchor(token_id)
```

#### 🟡 WARNING: No Async Network Requests in Feed Parsing
**Severity:** WARNING  
**Impact:** Blocking behavior in command handlers

```python
# commands/news.py - CURRENT (blocking)
for u in feeds:
    hit = _fetch_one(u)  # Synchronous request
    if hit:
        ...

# SHOULD USE: aiohttp for async requests
import aiohttp

async def _fetch_one_async(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as r:
                root = ET.fromstring(await r.text())
                # ... parse
    except Exception as e:
        logger.warning(f"Feed fetch failed: {e}")
        return None
```

#### 🟡 WARNING: No Connection Pooling
**Severity:** WARNING  
**Impact:** Inefficient resource use

- `requests` library creates new connections per request
- **Fix:** Use `requests.Session()` or better yet, `aiohttp`

#### 🟡 WARNING: Media Loaded on Every Command
**Severity:** WARNING  
**Impact:** Redundant file I/O

```python
# services/ritual.py - CURRENT
MEDIA = load_media_bank()  # Loaded at module import time - OK
# BUT in ritual_time.py:
def _pick_tip():
    try:
        bank = load_media_bank()  # ← Reloading on every ritual!
        ...

# SHOULD REUSE: from services.ritual import MEDIA
```

---

## 5. DEPLOYMENT & DEVOPS 🔴

### Issues

#### 🔴 CRITICAL: No Docker Support
**Severity:** CRITICAL  
**Impact:** Difficult to deploy consistently

**Missing:** `Dockerfile`, `.dockerignore`

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs data

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "app.py"]
```

#### 🔴 CRITICAL: No Graceful Shutdown Handler
**Severity:** CRITICAL  
**Impact:** Data loss, incomplete operations

```python
# app.py - ADD signal handling
import signal
import sys

async def shutdown(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    await app.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    app.run_polling(drop_pending_updates=True)
```

#### 🔴 CRITICAL: No Health Check Mechanism
**Severity:** CRITICAL  
**Impact:** Cannot monitor bot status in production

**Missing:** Health check endpoint or status file

```python
# Add health check command
@app.add_handler(CommandHandler("health", health_check))
async def health_check(update, context):
    logger.info("Health check requested")
    await update.message.reply_text("🟢 Bot is healthy")
```

#### 🟡 WARNING: Missing Logging Directory Setup
**Severity:** WARNING  
**Impact:** Crashes if `logs/` doesn't exist

```python
# app.py - ADD
import os
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
```

#### 🟡 WARNING: No Restart Policy Defined
**Severity:** WARNING  
**Impact:** Bot doesn't restart on crash

**Fix:** Use supervisor, systemd, or Docker restart policy

```ini
# /etc/systemd/system/toka.service (systemd)
[Unit]
Description=Toka 420 Time Bot
After=network.target

[Service]
Type=simple
User=toka
WorkingDirectory=/opt/toka
ExecStart=/opt/toka/.venv/bin/python app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 🟡 WARNING: Data Directory Not Backed Up
**Severity:** WARNING  
**Impact:** Loss of logs, state

- **Consider:** Volume mounts for `data/` and `logs/` directories
- **Consider:** Daily backups of `data/state.json`

#### 🟡 WARNING: No Version Pinning in requirements.txt
**Severity:** WARNING  
**Impact:** Dependency drift, reproducibility issues

```txt
# CURRENT
python-telegram-bot==20.3
requests==2.31.0

# BETTER - Pin all transitive deps
pip freeze > requirements.txt
```

---

## 6. MONITORING & OBSERVABILITY 🔴

### Issues

#### 🔴 CRITICAL: No Metrics Collection
**Severity:** CRITICAL  
**Impact:** Cannot measure bot health

**Missing:**
- Command invocation counts
- API response times
- Error rates
- Ritual execution success rates

**Fix:** Add prometheus metrics

```python
from prometheus_client import Counter, Histogram, CollectorRegistry

registry = CollectorRegistry()
commands_total = Counter(
    'bot_commands_total', 'Total commands', ['command'], registry=registry
)
api_duration = Histogram(
    'api_request_duration_seconds', 'API request duration', registry=registry
)

# In command handlers:
commands_total.labels(command='news').inc()
```

#### 🟡 WARNING: No Uptime Monitoring
**Severity:** WARNING  
**Impact:** Silent failures

- Consider: cron job to check bot every 5 minutes
- Consider: Monitoring service (Uptime Robot, etc.)

---

## 7. TESTING 🔴

### Issues

#### 🔴 CRITICAL: No Tests Exist
**Severity:** CRITICAL  
**Impact:** Cannot ensure reliability

**Missing:**
- Unit tests for parsing functions
- Integration tests for command handlers
- Mock tests for external APIs

```python
# tests/test_services.py
import pytest
from services.dexscreener import _format_anchor

def test_format_anchor():
    pair = {
        "priceUsd": "0.00123456",
        "priceChange": {"h24": 5.5},
        "volume": {"h24": 50000},
        "baseToken": {"symbol": "WEED"},
        "chainId": "solana",
        "dexId": "raydium"
    }
    result = _format_anchor(pair)
    assert result["symbol"] == "WEED"
    assert result["price"] == "$0.001235"
    assert result["change24"] == "+5.50%"
```

---

## PRIORITY FIX LIST

### 🔴 CRITICAL (Fix Immediately)
1. Add logging throughout all modules
2. Fix environment variable validation
3. Add input validation to commands
4. Update `.env.example`
5. Create Dockerfile & deployment docs
6. Add graceful shutdown
7. Create health check mechanism

### 🟡 IMPORTANT (Fix Before Production)
8. Improve error handling (specific exception types)
9. Add async request handling
10. Add unit tests
11. Add metrics collection
12. Set up restart policy
13. Create backup strategy

---

## RECOMMENDED DEPLOYMENT CHECKLIST

- [ ] All CRITICAL issues fixed
- [ ] Logging configured (file + stdout)
- [ ] `.env.example` matches actual usage
- [ ] Health check endpoint working
- [ ] Docker image builds successfully
- [ ] Systemd service file created
- [ ] Log rotation configured
- [ ] Backup cron job set up
- [ ] Monitoring alert configured
- [ ] Staging deployment successful
- [ ] Load test completed
- [ ] On-call runbook created

---

## ESTIMATED EFFORT

| Category | Effort | Priority |
|----------|--------|----------|
| Logging & Error Handling | 4h | CRITICAL |
| Config & Validation | 2h | CRITICAL |
| Input Sanitization | 1h | CRITICAL |
| Deployment (Docker/Systemd) | 3h | CRITICAL |
| Testing | 4h | HIGH |
| Performance Optimization | 2h | MEDIUM |
| Monitoring Setup | 3h | HIGH |

**Total Estimated Effort: 19 hours**

---

## NEXT STEPS

1. **Week 1:** Fix all CRITICAL issues (logging, config, security)
2. **Week 1:** Add unit tests for core services
3. **Week 2:** Set up Docker & deployment infrastructure
4. **Week 2:** Add monitoring & alerting
5. **Week 3:** Staging deployment & load testing
6. **Week 3:** Production deployment

---

*Report generated: 2026-01-15*  
*Next review: After CRITICAL fixes + staging deployment*
