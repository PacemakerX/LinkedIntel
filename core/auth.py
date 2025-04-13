# core/auth.py
import json
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import LINKEDIN_LOGIN_URL, DATA_DIR

class LinkedInAuth:
    def __init__(self):
        self.cookies_path = Path(DATA_DIR) / "cookies.json"
        
    def login(self, driver):
        """
        Log in to LinkedIn using saved cookies or manual login
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            bool: True if login successful, False otherwise
        """
        print("Attempting to log in to LinkedIn...")
        
        # First try to use saved cookies
        if self.has_saved_cookies():
            return self.login_with_cookies(driver)
        else:
            return self.manual_login(driver)
    
    def has_saved_cookies(self):
        """Check if saved cookies exist"""
        return self.cookies_path.exists() and self.cookies_path.stat().st_size > 0
    
    def login_with_cookies(self, driver):
        """Try to log in using saved cookies"""
        try:
            print("Attempting to log in with saved cookies...")
            
            # Load cookies from file
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
            
            # First navigate to LinkedIn domain to set cookies
            driver.get("https://www.linkedin.com")
            
            # Add cookies to browser session
            for cookie in cookies:
                # Some cookie attributes might cause issues, so let's use only what's needed
                try:
                    driver.add_cookie({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain']
                    })
                except Exception as e:
                    print(f"Error adding cookie: {e}")
            
            # Check if we're logged in by looking for the feed
            if "feed" in driver.current_url:
                print("Successfully logged in with cookies!")
                return True
            else:
                print("Cookie login failed. Falling back to manual login.")
                return self.manual_login(driver)
                
        except Exception as e:
            print(f"Cookie login error: {e}")
            return self.manual_login(driver)
    
    def manual_login(self, driver):
        """Manual login flow with user interaction"""
        try:
            print("Please log in manually in the browser window...")
            
            # Navigate to login page
            driver.get(LINKEDIN_LOGIN_URL)
            
            # Wait for manual login
            print("Waiting for you to log in manually...")
            wait = WebDriverWait(driver, 300)  # 5 minutes timeout
            wait.until(EC.url_contains("/feed/"))
            
            print("Successfully logged in manually!")
            
            # Save cookies for future sessions
            self.save_cookies(driver)
            
            return True
            
        except Exception as e:
            print(f"Manual login error: {e}")
            return False
    
    def save_cookies(self, driver):
        """Save browser cookies to file"""
        try:
            cookies = driver.get_cookies()
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f)
            print("Cookies saved successfully!")
        except Exception as e:
            print(f"Error saving cookies: {e}")

    def logout(self, driver):
        """Log out from LinkedIn"""
        try:
            # Navigate to the logout URL
            driver.get("https://www.linkedin.com/m/logout/")
            time.sleep(2)
            
            # Delete saved cookies
            if self.cookies_path.exists():
                self.cookies_path.unlink()
                
            return True
        except Exception as e:
            print(f"Logout error: {e}")
            return False