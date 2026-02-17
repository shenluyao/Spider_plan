from zdbk.utils import load_config, ensure_dir, print_browser_logs
from zdbk.browser import init_browser
from zdbk.login import login
from zdbk.data import fetch_training_plans
from zdbk.colors import print_info, print_success, print_error
import sys

def main():
    print_info("Starting ZDBK fetch script...")

    # Load configuration
    config = load_config()
    if not config:
        print_error("Configuration failed to load. Exiting.")
        return

    # Ensure output directory
    output_dir = config.get("output_dir", "./output")
    ensure_dir(output_dir)

    # Initialize Browser
    driver = init_browser(config)
    if not driver:
        print_error("Browser initialization failed. Exiting.")
        return

    try:
        # Login
        login(driver, config)

        # Fetch Data and Save PDFs
        fetch_training_plans(driver, config)

        print_success("All tasks completed.")

    except Exception as e:
        print_error(f"An unhandled exception occurred: {e}")
        if driver:
            print_browser_logs(driver)

    finally:
        if driver:
           driver.quit()
           print_info("Browser closed.")

if __name__ == "__main__":
    main()