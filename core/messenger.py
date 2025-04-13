# core/messenger.py
import time
import random
import json
from pathlib import Path
import openai
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import (
    DATA_DIR, 
    OPENAI_API_KEY, 
    OPENAI_MODEL,
    MIN_ACTION_DELAY,
    MAX_ACTION_DELAY,
    MAX_MESSAGES_PER_DAY
)

# Set OpenAI API key from config
openai.api_key = OPENAI_API_KEY

class LinkedInMessenger:
    def __init__(self):
        self.history_path = Path(DATA_DIR) / "history.json"
        self.templates_path = Path(DATA_DIR) / "templates" / "messages.txt"
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
    
    def send_messages_to_connections(self, driver, max_messages=None, connection_filter=None):
        """
        Send messages to LinkedIn connections
        
        Args:
            driver: Selenium WebDriver instance
            max_messages: Maximum number of messages to send
            connection_filter: Optional filter criteria for connections
            
        Returns:
            dict: Results including number of messages sent
        """
        max_messages = max_messages or MAX_MESSAGES_PER_DAY
        
        # Check how many messages we've already sent today
        today_messages = self._count_todays_messages()
        if today_messages >= MAX_MESSAGES_PER_DAY:
            print(f"Already sent {today_messages} messages today. Daily limit reached.")
            return {"sent": 0, "skipped": 0, "errors": ["Daily limit reached"]}
        
        remaining_messages = MAX_MESSAGES_PER_DAY - today_messages
        max_messages = min(max_messages, remaining_messages)
        
        print(f"Starting messaging campaign. Will send up to {max_messages} messages.")
        
        # Navigate to connections page
        driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
        
        # Wait for connections to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mn-connection-card"))
            )
        except TimeoutException:
            print("Timeout waiting for connections to load")
            return {"sent": 0, "skipped": 0, "errors": ["Timeout waiting for connections"]}
        
        results = {
            "sent": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Get connection elements
        connection_cards = driver.find_elements(By.CSS_SELECTOR, ".mn-connection-card")
        print(f"Found {len(connection_cards)} connections")
        
        for card in connection_cards:
            if results["sent"] >= max_messages:
                print(f"Reached maximum messages limit ({max_messages})")
                break
            
            try:
                # Extract connection data
                connection_data = self._extract_connection_data(card)
                connection_id = connection_data.get("profile_id")
                
                if not connection_id:
                    results["skipped"] += 1
                    continue
                
                # Apply filter if provided
                if connection_filter and not self._apply_filter(connection_data, connection_filter):
                    print(f"Connection {connection_data.get('name', 'unknown')} filtered out")
                    results["skipped"] += 1
                    continue
                
                # Check if we've already messaged this connection recently
                if self._has_recent_message(connection_id):
                    print(f"Already messaged {connection_data.get('name', 'unknown')} recently")
                    results["skipped"] += 1
                    continue
                
                # Click on the "Message" button
                message_button = card.find_element(By.CSS_SELECTOR, "button[aria-label^='Message']")
                driver.execute_script("arguments[0].click();", message_button)
                
                # Wait for message box to appear
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".msg-form__contenteditable"))
                    )
                except TimeoutException:
                    results["errors"].append(f"Timeout waiting for message box for {connection_data.get('name', 'unknown')}")
                    results["skipped"] += 1
                    continue
                
                # Generate message
                message_text = self._generate_message(connection_data)
                
                # Type message with human-like delays
                message_input = driver.find_element(By.CSS_SELECTOR, ".msg-form__contenteditable")
                for char in message_text:
                    message_input.send_keys(char)
                    time.sleep(random.uniform(0.01, 0.08))  # Slight delay between keystrokes
                
                self._random_delay(1, 2)
                
                # Send message
                send_button = driver.find_element(By.CSS_SELECTOR, "button.msg-form__send-button")
                driver.execute_script("arguments[0].click();", send_button)
                
                # Wait for message to be sent
                self._random_delay(2, 4)
                
                # Close the message dialog
                try:
                    close_button = driver.find_element(By.CSS_SELECTOR, "button[data-control-name='overlay.close_conversation_window']")
                    driver.execute_script("arguments[0].click();", close_button)
                except NoSuchElementException:
                    # If close button not found, try clicking outside the dialog
                    driver.execute_script("document.querySelector('.msg-overlay-bubble-header').click();")
                
                # Record the message
                self._record_message(connection_data, message_text)
                
                print(f"Sent message to {connection_data.get('name', 'unknown')}")
                results["sent"] += 1
                
                # Random delay between messages
                self._random_delay(3, 7)
                
            except Exception as e:
                error_msg = f"Error sending message: {str(e)}"
                print(error_msg)
                results["errors"].append(error_msg)
                results["skipped"] += 1
        
        print(f"Messaging campaign completed. Sent: {results['sent']}, Skipped: {results['skipped']}")
        return results
    
    def _extract_connection_data(self, connection_card):
        """Extract connection data from a connection card element"""
        try:
            # Extract name
            try:
                name_element = connection_card.find_element(By.CSS_SELECTOR, ".mn-connection-card__name")
                name = name_element.text.strip()
            except NoSuchElementException:
                name = "Unknown"
            
            # Extract profile URL and ID
            try:
                link_element = connection_card.find_element(By.CSS_SELECTOR, ".mn-connection-card__link")
                profile_url = link_element.get_attribute("href")
                # Extract profile ID from URL
                profile_id = profile_url.split("/in/")[1].split("/")[0] if "/in/" in profile_url else None
            except NoSuchElementException:
                profile_url = ""
                profile_id = None
            
            # Extract occupation
            try:
                occupation_element = connection_card.find_element(By.CSS_SELECTOR, ".mn-connection-card__occupation")
                occupation = occupation_element.text.strip()
            except NoSuchElementException:
                occupation = ""
            
            # Extract connection time (if available)
            try:
                time_element = connection_card.find_element(By.CSS_SELECTOR, ".time-badge")
                connected_time = time_element.text.strip()
            except NoSuchElementException:
                connected_time = ""
            
            return {
                "name": name,
                "profile_id": profile_id,
                "profile_url": profile_url,
                "occupation": occupation,
                "connected_time": connected_time
            }
        except Exception as e:
            print(f"Error extracting connection data: {e}")
            return {}

    def _apply_filter(self, connection_data, connection_filter):
        """Apply the given filter to the connection data"""
        # Example filter: Only message connections who are in a certain industry or occupation
        if connection_filter.get("occupation") and connection_data.get("occupation") != connection_filter["occupation"]:
            return False
        return True
    
    def _has_recent_message(self, connection_id):
        """Check if a message has been sent to this connection recently"""
        return connection_id in self.action_history["messages"] and self.action_history["messages"][connection_id].get("sent_today", False)

    def _generate_message(self, connection_data):
        """Generate a message to send to the connection"""
        # Load templates if available
        try:
            with open(self.templates_path, 'r') as f:
                templates = f.readlines()
        except FileNotFoundError:
            templates = ["Hi {{name}}, I hope you're doing well! Let's connect and chat about opportunities."]

        # Pick a random template and personalize it
        template = random.choice(templates).strip()
        message = template.replace("{{name}}", connection_data.get("name", "there"))

        # Use OpenAI to refine or generate a message based on the template
        refined_message = self._refine_message_with_openai(message, connection_data)
        
        return refined_message

    def _refine_message_with_openai(self, message, connection_data):
        """Use OpenAI API to refine or personalize the message"""
        try:
            prompt = f"Refine the following message to sound more engaging and professional: {message}"
            response = openai.Completion.create(
                model=OPENAI_MODEL,
                prompt=prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7
            )
            refined_message = response.choices[0].text.strip()
            return refined_message
        except Exception as e:
            print(f"Error generating message with OpenAI: {e}")
            return message  # Fallback to the original message if OpenAI fails
    
    def _record_message(self, connection_data, message_text):
        """Record the sent message in the action history"""
        connection_id = connection_data.get("profile_id")
        if connection_id:
            self.action_history["messages"][connection_id] = {
                "message": message_text,
                "sent_today": True
            }
            self._save_history()
    
    def _count_todays_messages(self):
        """Count how many messages have been sent today"""
        today = time.strftime("%Y-%m-%d")
        count = 0
        for connection_id, action in self.action_history["messages"].items():
            if action.get("sent_today"):
                count += 1
        return count

    def _random_delay(self, min_seconds, max_seconds):
        """Wait for a random period to simulate human-like interaction"""
        time.sleep(random.uniform(min_seconds, max_seconds))
