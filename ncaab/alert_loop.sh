#!/usr/bin/env bash
# NCAAM-only line check loop (Nov 6, 2026, NCAAM live move; plan: betting-goals/plans/2026-11-06_NCAAM_LIVE_MOVE.md).
# Same cadence as nba-mixed-model/alert_loop.sh: ncaab/live_alert.py every 5 minutes (at the 5-minute mark + 20 s) for about 50 minutes,
# saving after each check. GitHub's scheduler often starts "every 10 minutes" jobs 30-60 minutes apart, so each run keeps itself going.
# SHADOW: while NCAAM_SHADOW=1 (the default) NTFY_TOPIC is removed, so live_alert.py records "would have sent" in live_bets.csv
# (sent=False) and sends nothing. NTFY_TOPIC is already set as a secret in this repo, so this unset is what keeps the shadow silent.
# Cutover (Phase 2, Jeffrey present): set NCAAM_SHADOW: "0" in ncaab-alerts.yml and pass the secret.
set -u
if [ "${NCAAM_SHADOW:-1}" = "1" ]; then unset NTFY_TOPIC; echo "SHADOW mode: no alerts are sent."; fi
git config user.name "ncaam-bot"
git config user.email "actions@users.noreply.github.com"
START=$(date +%s)
LIMIT=${LOOP_SECONDS:-3000}

busy() {   # 0 if the NCAAM daily job (which also writes ncaab/state) is running
  n=$(gh run list --workflow ncaab.yml --status in_progress --json databaseId --jq length 2>/dev/null || echo 0)
  q=$(gh run list --workflow ncaab.yml --status queued --json databaseId --jq length 2>/dev/null || echo 0)
  [ "${n:-0}" != "0" ] || [ "${q:-0}" != "0" ]
}

save() {
  for f in ncaab/state/dk_lines.csv ncaab/state/live_evals.csv ncaab/state/live_bets.csv ncaab/state/live_poll.json ncaab/state/live_stop.txt ncaab/state/heartbeat_alert.txt; do
    if [ -f "$f" ]; then git add "$f"; fi
  done
  git diff --cached --quiet && return 0
  git commit -q -m "NCAAM alerts $(TZ=America/New_York date '+%F %H:%M')"
  for i in 1 2 3; do
    if git pull --rebase --autostash -q && git push -q; then return 0; fi
    git rebase --abort 2>/dev/null
    sleep 5
  done
  echo "Could not save this check; resetting to the latest saved state."
  git fetch -q && git reset -q --hard origin/main
}

while :; do
  while busy; do echo "NCAAM daily run is saving; waiting."; sleep 30; done
  git pull --rebase --autostash -q || { git rebase --abort 2>/dev/null; git fetch -q; git reset -q --hard origin/main; }
  echo "=== check at $(TZ=America/New_York date '+%F %H:%M:%S') ET ==="
  if timeout 120 python ncaab/live_alert.py .; then date -u +%Y-%m-%dT%H:%M:%SZ > ncaab/state/heartbeat_alert.txt; else echo "NCAAM line check failed; trying again next time."; fi
  while busy; do echo "NCAAM daily run is saving; waiting."; sleep 30; done
  save
  NOW=$(date +%s)
  [ $((NOW - START + 300)) -ge "$LIMIT" ] && break
  TARGET=$((NOW + 300 - NOW % 300 + 20))
  WAIT=$((TARGET - $(date +%s))); [ "$WAIT" -gt 0 ] && sleep "$WAIT"
done
echo "Loop finished after $(( ($(date +%s) - START) / 60 )) minutes."
