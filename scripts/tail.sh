#!/usr/bin/env bash
set -euo pipefail
[ -f ./data/bot.log ] || type NUL > ./data/bot.log
tail -f ./data/bot.log
