# MCP Flight Search - Auto Update Configuration

## Auto-Update Setup

This skill is configured to automatically check for updates from the GitHub repository.

### Update Script

Location: `auto_update.sh`

The script:
- Checks GitHub repo for new commits
- Pulls updates if available
- Reinstalls Python package with updated dependencies
- Logs all actions to `update.log`

### Manual Update

Run anytime:
```bash
cd /Users/vecsatfoxmailcom/.gemini/antigravity/skills/mcp-flight-search
./auto_update.sh
```

### Automatic Updates (Optional)

To enable automatic daily checks, add to crontab:
```bash
# Check for updates daily at 3 AM
0 3 * * * /Users/vecsatfoxmailcom/.gemini/antigravity/skills/mcp-flight-search/auto_update.sh
```

Or run manually when starting a new session.

### Update Log

Check `update.log` to see update history and status.

### Repository

- **Source**: https://github.com/arjunprabhulal/mcp-flight-search
- **Branch**: main
- **Current tracking**: origin/main

---

**Installed**: 2026-02-05 by Antigravity  
**Auto-update enabled**: Yes (manual trigger)
