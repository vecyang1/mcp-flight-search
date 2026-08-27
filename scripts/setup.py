import os
import json
import sys

def setup_mcp_config():
    """Generates a local .mcp.json file with dynamic paths."""
    
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(skill_dir, '.mcp.json')
    env_path = os.path.join(skill_dir, '.env')
    
    print(f"Setting up MCP Config for: {skill_dir}")
    
    # default config template
    config = {
      "mcpServers": {
        "flight-search": {
          "command": "python3",
          "args": [
            "-m",
            "mcp_flight_search.server"
          ],
          "cwd": skill_dir,
          "env": {}
        }
      }
    }
    
    # Check for .env file first
    api_key = None
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("SERP_API_KEY="):
                    api_key = line.strip().split('=')[1]
                    print("Found SERP_API_KEY in .env")
                    break
    
    # If not in .env, ask user (not applicable for auto-run, but good for interactive)
    if not api_key:
        # Check if we already have it in existing .mcp.json
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    old_config = json.load(f)
                    api_key = old_config.get("mcpServers", {}).get("flight-search", {}).get("env", {}).get("SERP_API_KEY")
            except:
                pass

    if not api_key:
        print("WARNING: SERP_API_KEY not found. Please add it to .env or .mcp.json manually.")
        api_key = "YOUR_API_KEY_HERE"
        
    config["mcpServers"]["flight-search"]["env"]["SERP_API_KEY"] = api_key
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    print(f"Generated {config_path} with CWD: {skill_dir}")

if __name__ == "__main__":
    setup_mcp_config()
