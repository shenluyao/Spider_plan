import json
import os
from .colors import print_error, print_info, print_warning

def load_config(config_path="config.json"):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"Config file not found: {config_path}")
        return None
    except json.JSONDecodeError:
        print_error(f"Error decoding config file: {config_path}")
        return None

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def print_browser_logs(driver):
    try:
        logs = driver.get_log('browser')
        if logs:
            print_info("----- Browser Console Logs (Last 20) -----")
            for log in logs[-20:]:  # Print only last 20 logs to avoid spam
                level = log.get('level', 'INFO')
                message = log.get('message', '')
                if level == 'SEVERE':
                    print_error(f"[{level}] {message}")
                elif level == 'WARNING':
                    print_warning(f"[{level}] {message}")
                else:
                    print(f"[{level}] {message}")
            print_info("------------------------------------------")
        else:
            print_info("No browser logs captured.")
    except Exception as e:
        print_warning(f"Could not retrieve browser logs: {e}")
