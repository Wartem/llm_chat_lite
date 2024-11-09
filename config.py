# config.py
import json
import os

DEFAULT_CONFIG = {
    "theme": "dark",  # or "bright"
    "themes": {
        "dark": "/static/style.css",
        "bright": "/static/bright_style.css"
    }
}

CONFIG_PATH = "config.json"

def ensure_config_exists():
    """Create config file if it doesn't exist"""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        print(f"Created new config file at {CONFIG_PATH}")

def load_config():
    ensure_config_exists()
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            # Validate config has required fields
            if not all(key in config for key in DEFAULT_CONFIG.keys()):
                print("Invalid config file, resetting to default")
                save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG
            return config
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading config: {e}, using default")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def get_current_theme():
    config = load_config()
    theme_name = config.get('theme', 'dark')
    return config['themes'].get(theme_name, DEFAULT_CONFIG['themes']['dark'])

def set_theme(theme_name):
    if theme_name not in ['dark', 'bright']:
        raise ValueError("Invalid theme name. Use 'dark' or 'bright'")
    
    config = load_config()
    config['theme'] = theme_name
    save_config(config)