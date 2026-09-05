#!/usr/bin/env bash
set -euo pipefail
APP="${HOME}/Documents/Francabel/francabel.py"
PY="$(command -v python3)"
LINE="0 3 * * * CRON_TZ=America/New_York ${PY} ${APP} --run-desk >> ${HOME}/.francabel-desk.log 2>&1"
(crontab -l 2>/dev/null | grep -v Francabel | grep -v francabel.py || true; echo "$LINE") | crontab -
echo "Installed 3:00am Eastern Francabel desk cron."
crontab -l | grep francabel || true
