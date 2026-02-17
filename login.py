from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .colors import print_info, print_success, print_error
import time

def login(driver, config):
    print_info("Navigating to login page...")
    login_url = "http://zdbk.zju.edu.cn/" # Usually redirects to unified login
    driver.get(login_url)

    try:
        # Wait for page load
        time.sleep(3)

        # Try to click SSO login image if present (User requirment)
        try:
            sso_element = driver.find_element(By.ID, "ssodl")
            print_info("Found SSO login image (id='ssodl'), clicking...")
            sso_element.click()
            time.sleep(3) # Wait for redirect
        except Exception:
            pass
        
        # Check if we are on the ZJU Unified Identity page
        if "zjuam.zju.edu.cn" in driver.current_url:
            print_info("Detected ZJU Unified Identity Authentication page.")
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_input = driver.find_element(By.ID, "password")

            username_input.clear()
            username_input.send_keys(config['username'])
            password_input.clear()
            password_input.send_keys(config['password'])

            # Click login button
            login_btn = driver.find_element(By.ID, "dl")
            login_btn.click()

        else:
            # Fallback for direct system login if exists
            print_info("Attempting generic login form detection...")
            username_input = driver.find_element(By.ID, "yhm") # Common in ZFSoft
            password_input = driver.find_element(By.ID, "mm")

            username_input.send_keys(config['username'])
            password_input.send_keys(config['password'])

            login_btn = driver.find_element(By.ID, "dl")
            login_btn.click()

        # Check for success
        # Usually redirects back to index
        time.sleep(5)
        print_success("Login action performed. Please verify if successful (e.g. check for Captcha if failed).")

    except Exception as e:
        print_error(f"Login failed: {e}")
        print_info("Please log in manually in the browser window within 60 seconds.")
        time.sleep(60)

