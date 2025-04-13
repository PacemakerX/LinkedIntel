# core/connect.py
import time
import random
import json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import (
    DATA_DIR,
    MIN_ACTION_DELAY,
    MAX_ACTION_DELAY,
    MAX_CONNECTION_REQUESTS_PER_DAY
)

class LinkedInConnect:
    def __init__(self):
        self.history_path = Path(DATA_DIR) / "history.json"
        self.action_history = self._load_history()
    
    def _load_history(self):
        """Load interaction history from file"""
        if self.history_path.exists():
            try:
                with open(self.history_path, 'r') as f:
                    return json.load(f)
            except:
                return {"likes": {}, "comments": {}, "connections": {}, "messages": {}}
        else:
            return {"likes": {}, "comments": {}, "connections": {}, "messages": {}}
    
    def _save_history(self):
        """Save interaction history to file"""
        with open(self.history_path, 'w') as f:
            json.dump(self.action_history, f)
    
    def search_and_connect(self, driver, search_url, max_connections=None):
        """
        Search for LinkedIn profiles and send connection requests
        
        Args:
            driver: Selenium WebDriver instance
            search_url: LinkedIn search URL with filters
            max_connections: Maximum number of connection requests to send
            
        Returns:
            dict: Results including number of requests sent
        """
        max_connections = max_connections or MAX_CONNECTION_REQUESTS_PER_DAY
        
        # Check how many connections we've already sent today
        today_connections = self._count_todays_connections()
        if today_connections >= MAX_CONNECTION_REQUESTS_PER_DAY:
            print(f"Already sent {today_connections} connection requests today. Daily limit reached.")
            return {"sent": 0, "skipped": 0, "errors": ["Daily limit reached"]}
        
        remaining_connections = MAX_CONNECTION_REQUESTS_PER_DAY - today_connections
        max_connections = min(max_connections, remaining_connections)
        
        print(f"Starting connection campaign. Will send up to {max_connections} requests.")
        
        # Navigate to search URL
        driver.get(search_url)
        
        # Wait for search results to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".reusable-search__result-container"))
            )
        except TimeoutException:
            print("Timeout waiting for search results to load")
            return {"sent": 0, "skipped": 0, "errors": ["Timeout waiting for search results"]}
        
        results = {
            "sent": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Get search result elements
        search_results = driver.find_elements(By.CSS_SELECTOR, ".reusable-search__result-container")
        print(f"Found {len(search_results)} search results")
        
        for result in search_results:
            if results["sent"] >= max_connections:
                print(f"Reached maximum connections limit ({max_connections})")
                break
            
            try:
                # Extract profile data
                profile_data = self._extract_profile_data(result)
                profile_id = profile_data.get("profile_id")
                
                if not profile_id:
                    results["skipped"] += 1
                    continue
                
                # Check if we've already connected with this profile
                if self._has_connection_request(profile_id):
                    print(f"Already sent connection request to {profile_data.get('name', 'unknown')}")
                    results["skipped"] += 1
                    continue
                
                # Find connect button
                connect_button = self._find_connect_button(result)
                if not connect_button:
                    results["skipped"] += 1
                    continue
                
                # Click connect button
                driver.execute_script("arguments[0].click();", connect_button)
                self._random_delay(1, 2)
                
                # Check if there's a "Add a note" option
                try:
                    add_note_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Add a note']"))
                    )
                    
                    # Click "Add a note" button
                    driver.execute_script("arguments[0].click();", add_note_button)
                    self._random_delay(1, 2)
                    
                    # Write a personalized note
                    note_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".send-invite__custom-message"))
                    )
                    
                    personalized_note = self._create_connection_note(profile_data)
                    
                    # Type connection note with human-like delays
                    for char in personalized_note:
                        note_input.send_keys(char)
                        time.sleep(random.uniform(0.01, 0.08))
                    
                    self._random_delay(1, 2)
                    
                    # Find and click the send button
                    send_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send invitation']")
                    driver.execute_script("arguments[0].click();", send_button)
                    
                except TimeoutException:
                    # No "Add a note" option, just send the connection request
                    try:
                        send_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send now']")
                        driver.execute_script("arguments[0].click();", send_button)
                    except NoSuchElementException:
                        results["errors"].append(f"Could not find send button for {profile_data.get('name', 'unknown')}")
                        results["skipped"] += 1
                        continue
                
                # Record the connection request
                self._record_connection_request(profile_data)
                
                print(f"Sent connection request to {profile_data.get('name', 'unknown')}")
                results["sent"] += 1
                
                # Random delay between connection requests
                self._random_delay(3, 7)
                
            except Exception as e:
                error_msg = f"Error sending connection request: {str(e)}"
                print(error_msg)
                results["errors"].append(error_msg)
                results["skipped"] += 1
        
        print(f"Connection campaign completed. Sent: {results['sent']}, Skipped: {results['skipped']}")
        return results
    
    def _extract_profile_data(self, result_element):
        """Extract profile data from search result element"""
        try:
            # Extract name
            try:
                name_element = result_element.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                name = name_element.text.strip()
                profile_url = name_element.get_attribute("href")
                # Extract profile ID from URL
                profile_id = profile_url.split("/in/")[1].split("/")[0] if "/in/" in profile_url else None
            except NoSuchElementException:
                name = "Unknown"
                profile_url = ""
                profile_id = None
            
            # Extract headline
            try:
                headline_element = result_element.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                headline = headline_element.text.strip()
            except NoSuchElementException:
                headline = ""
            
            # Extract company/location
            try:
                company_element = result_element.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                company = company_element.text.strip()
            except NoSuchElementException:
                company = ""
            
            return {
                "name": name,
                "profile_id": profile_id,
                "profile_url": profile_url,
                "headline": headline,
                "company": company
            }
            
        except Exception as e:
            print(f"Error extracting profile data: {e}")
            return {}
    
    def _find_connect_button(self, result_element):
        """Find the connect button in a search result"""
        try:
            # Try the primary connect button
            connect_buttons = result_element.find_elements(By.CSS_SELECTOR, 
                "button.artdeco-button[aria-label^='Connect with']")
            
            if connect_buttons:
                return connect_buttons[0]
            
            # Try the secondary connect button (might be in a dropdown)
            more_buttons = result_element.find_elements(By.CSS_SELECTOR, 
                "button.artdeco-dropdown__trigger[aria-label^='More actions']")
            
            if more_buttons:
                more_button = more_buttons[0]
                more_button.click()
                time.sleep(1)
                
                # Find connect option in dropdown
                connect_options = result_element.find_elements(By.CSS_SELECTOR, 
                    "div.artdeco-dropdown__content li button[aria-label^='Connect with']")
                
                if connect_options:
                    return connect_options[0]
            
            return None
            
        except Exception as e:
            print(f"Error finding connect button: {e}")
            return None
    
    def _create_connection_note(self, profile_data):
        """Create a personalized connection note"""
        name = profile_data.get("name", "").split(" ")[0]  # Get first name
        
        templates = [
            f"Hi {name}, I noticed your profile while browsing LinkedIn and thought we could connect. Looking forward to sharing insights about our industries!",
            f"Hello {name}, I'm expanding my professional network and would love to connect with you. Hope to learn from your experience in {profile_data.get('headline', 'your field')}.",
            f"Hi {name}, I came across your profile and was impressed by your experience at {profile_data.get('company', 'your company')}. I'd be glad to connect with you."
        ]
        
        return random.choice(templates)
    
    def _has_connection_request(self, profile_id):
        """Check if we've already sent a connection request to this profile"""
        return profile_id in self.action_history.get("connections", {})
    
    def _record_connection_request(self, profile_data):
        """Record a connection request"""
        profile_id = profile_data.get("profile_id")
        
        if not profile_id:
            return
        
        if "connections" not in self.action_history:
            self.action_history["connections"] = {}
            
        self.action_history["connections"][profile_id] = {
            "timestamp": time.time(),
            "details": profile_data
        }
        
        self._save_history()
    
    def _count_todays_connections(self):
        """Count how many connection requests we've sent today"""
        today_start = time.time() - (24 * 60 * 60)  # 24 hours ago
        
        count = 0
        for profile_id, data in self.action_history.get("connections", {}).items():
            if data.get("timestamp", 0) > today_start:
                count += 1
        
        return count
    
    def _random_delay(self, min_delay=None, max_delay=None):
        """Add a random delay to simulate human behavior"""
        min_delay = min_delay or MIN_ACTION_DELAY
        max_delay = max_delay or MAX_ACTION_DELAY
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)