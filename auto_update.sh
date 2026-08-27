#!/bin/bash
# Auto-update script for mcp-flight-search skill
# Checks GitHub repo for updates and pulls if available

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SKILL_DIR/update.log"

echo "[$(date)] Checking for updates..." >> "$LOG_FILE"

cd "$SKILL_DIR" || exit 1

# Fetch latest from GitHub
git fetch origin main 2>&1 >> "$LOG_FILE"

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date)] Updates found! Pulling changes..." >> "$LOG_FILE"
    
    # Pull updates
    git pull origin main 2>&1 >> "$LOG_FILE"
    
    # Reinstall package to update dependencies
    python3 -m pip install -e . --quiet 2>&1 >> "$LOG_FILE"
    
    echo "[$(date)] ✅ Successfully updated to latest version" >> "$LOG_FILE"
    echo "Updated mcp-flight-search skill"
else
    echo "[$(date)] Already up to date" >> "$LOG_FILE"
fi
