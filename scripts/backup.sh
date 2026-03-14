#!/usr/bin/env bash
# backup.sh — ClearClaim daily database backup
#
# Schedule via cron (runs at 02:00 every night):
#   0 2 * * * /path/to/clearclaim/scripts/backup.sh >> /var/log/clearclaim-backup.log 2>&1
#
# Retention:
#   7  daily backups   (YYYY-MM-DD)
#   4  weekly backups  (kept every Sunday)
#   3  monthly backups (kept on the 1st of each month)

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
# Load production env if available
if [ -f "$(dirname "$0")/../.env.prod" ]; then
  # shellcheck disable=SC1091
  set -a; source "$(dirname "$0")/../.env.prod"; set +a
fi

DB_URL="${DATABASE_URL:-postgresql://postgres:devpassword@localhost:5432/clearclaim_dev}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/clearclaim}"
TODAY=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)   # 1=Monday … 7=Sunday
DAY_OF_MONTH=$(date +%d)

mkdir -p "$BACKUP_DIR/daily" "$BACKUP_DIR/weekly" "$BACKUP_DIR/monthly"

# ── Daily backup ──────────────────────────────────────────────────────────────
DAILY_FILE="$BACKUP_DIR/daily/clearclaim-$TODAY.dump"
echo "[$(date -Iseconds)] Starting daily backup → $DAILY_FILE"
pg_dump --format=custom "$DB_URL" > "$DAILY_FILE"
echo "[$(date -Iseconds)] Daily backup complete ($(du -sh "$DAILY_FILE" | cut -f1))"

# ── Weekly (Sunday) ───────────────────────────────────────────────────────────
if [ "$DAY_OF_WEEK" -eq 7 ]; then
  cp "$DAILY_FILE" "$BACKUP_DIR/weekly/clearclaim-week-$TODAY.dump"
  echo "[$(date -Iseconds)] Weekly backup saved."
fi

# ── Monthly (1st of month) ────────────────────────────────────────────────────
if [ "$DAY_OF_MONTH" -eq "01" ]; then
  cp "$DAILY_FILE" "$BACKUP_DIR/monthly/clearclaim-month-$TODAY.dump"
  echo "[$(date -Iseconds)] Monthly backup saved."
fi

# ── Pruning ───────────────────────────────────────────────────────────────────
find "$BACKUP_DIR/daily"   -name "*.dump" -mtime +7  -delete
find "$BACKUP_DIR/weekly"  -name "*.dump" -mtime +28 -delete
find "$BACKUP_DIR/monthly" -name "*.dump" -mtime +92 -delete
echo "[$(date -Iseconds)] Pruning complete."
