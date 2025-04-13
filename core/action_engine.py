# core/action_engine.py
import time
import random
import json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from config import (
    DATA_DIR,
    MIN_ACTION_DELAY,
    MAX_ACTION_DELAY
)

class ActionEngine:
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

    def has_interacted_with_post(self, post_id, action_type):
        """Check if we've already interacted with this post"""
        return post_id in self.action_history.get(action_type, {})

    def record_interaction(self, post_id, action_type, details=None):
        """Record an interaction with a post"""
        if action_type not in self.action_history:
            self.action_history[action_type] = {}

        self.action_history[action_type][post_id] = {
            "timestamp": time.time(),
            "details": details or {}
        }

        self._save_history()

    def perform_actions(self, driver, post_data, analysis_result):
        """
        Perform actions on a post based on AI analysis

        Args:
            driver: Selenium WebDriver instance
            post_data: Dictionary with post information
            analysis_result: Dictionary with AI analysis results

        Returns:
            dict: Results of actions performed
        """
        post_id = post_data.get("post_id", "").split(":")[-1]
        post_element = post_data.get("post_element")

        results = {
            "liked": False,
            "commented": False,
            "comment_text": "",
            "errors": []
        }

        if not post_element:
            results["errors"].append("Post element not found")
            return results

        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_element)
            self._random_delay(0.5, 1.5)

            if (analysis_result.get("should_like", False) and
                not self.has_interacted_with_post(post_id, "likes")):

                if self.like_post(driver, post_element):
                    results["liked"] = True
                    self.record_interaction(post_id, "likes")

            if (analysis_result.get("should_comment", False) and
                analysis_result.get("comment_text") and
                not self.has_interacted_with_post(post_id, "comments")):

                comment_text = analysis_result.get("comment_text", "")
                if self.comment_on_post(driver, post_element, comment_text):
                    results["commented"] = True
                    results["comment_text"] = comment_text
                    self.record_interaction(post_id, "comments", {"text": comment_text})

        except Exception as e:
            error_msg = f"Error performing actions: {str(e)}"
            print(error_msg)
            results["errors"].append(error_msg)

        return results

    def like_post(self, driver, post_element):
        """
        Like a LinkedIn post

        Args:
            driver: Selenium WebDriver instance
            post_element: The post web element

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Look for all buttons that potentially represent the Like button
            buttons = post_element.find_elements(
                By.XPATH, ".//button[contains(@aria-label, 'Like') or contains(@aria-label, 'like')]"
            )

            for btn in buttons:
                aria_label = btn.get_attribute("aria-label") or ""
                is_pressed = btn.get_attribute("aria-pressed")

            # Only click if not already liked
            if "Like" in aria_label and is_pressed != "true":
                driver.execute_script("arguments[0].click();", btn)
                print("Liked post")
                self._random_delay()
                return True

            print("Post already liked or Like button not found")
            return False

        except Exception as e:
            print(f"Error liking post: {e}")
            return False


    def comment_on_post(self, driver, post_element, comment_text):
        """
        Comment on a LinkedIn post

        Args:
            driver: Selenium WebDriver instance
            post_element: The post web element
            comment_text: The text to comment

        Returns:
            bool: True if successful, False otherwise
        """
        try:
        # Open comment box if not already open
            comment_button = post_element.find_element(By.CSS_SELECTOR,
                "button.comment-button, button[data-control-name='comment']")
            driver.execute_script("arguments[0].click();", comment_button)
            self._random_delay()

            # Type comment
            comment_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor"))
            )
            for char in comment_text:
                comment_field.send_keys(char)
                time.sleep(random.uniform(0.01, 0.05))
            self._random_delay(1, 2)

            # Use the correct button selector (from your screenshot)
            post_button = post_element.find_element(
                By.CSS_SELECTOR, "button.comments-comment-box__submit-button--cr"
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
            self._random_delay(0.3, 0.6)
            driver.execute_script("arguments[0].click();", post_button)

            self._random_delay(2, 4)
            print(f"✅ Posted comment: {comment_text[:30]}...")
            return True

        except Exception as e:
            print(f"❌ Error commenting on post: {e}")
            return False

    def _random_delay(self, min_delay=None, max_delay=None):
        """Add a random delay to simulate human behavior"""
        min_delay = min_delay or MIN_ACTION_DELAY
        max_delay = max_delay or MAX_ACTION_DELAY
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
