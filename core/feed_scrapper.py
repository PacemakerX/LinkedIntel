import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import (
    LINKEDIN_FEED_URL, 
    MAX_POSTS_TO_SCRAPE, 
    MAX_SCROLL_ITERATIONS,
    MIN_SCROLL_DELAY,
    MAX_SCROLL_DELAY
)

class FeedScraper:
    def __init__(self):
        self.posts_scraped = 0
    
    def scrape_feed(self, driver):
        """
        Scrapes the LinkedIn feed for posts
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            list: List of dictionaries containing post data
        """
        print("Scraping LinkedIn feed...")
        
        # Navigate to feed
        driver.get(LINKEDIN_FEED_URL)
        
        # Wait for feed to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-shared-update-v2"))
            )
        except TimeoutException:
            print("Timeout waiting for feed to load")
            return []
        
        posts = []
        scroll_count = 0
        
        # Scroll and collect posts
        while (len(posts) < MAX_POSTS_TO_SCRAPE and 
               scroll_count < MAX_SCROLL_ITERATIONS):
            
            # Get all posts currently visible
            post_elements = driver.find_elements(By.CSS_SELECTOR, ".feed-shared-update-v2")
            
            for post_element in post_elements:
                # Skip posts we've already processed
                post_id = post_element.get_attribute("data-urn")
                if any(p.get("post_id") == post_id for p in posts):
                    continue
                
                try:
                    post_data = self._extract_post_data(driver, post_element)
                    if post_data and post_data["post_text"].strip():
                        posts.append(post_data)
                        print(f"Scraped post #{len(posts)}")
                        print(f"👤 Author: {post_data['author_name']}")
                        print(f"🔗 Profile: {post_data['author_link']}")
                        print(f"📝 Text: {post_data['post_text'][:200]}{'...' if len(post_data['post_text']) > 200 else ''}")
                        print(f"🔗 Post URL: {post_data['post_url']}")

                        # Stop scraping if we reach the max number of posts
                        if len(posts) >= MAX_POSTS_TO_SCRAPE:
                            break
                except Exception as e:
                    print(f"Error extracting post data: {e}")
            
            # Scroll down to load more posts
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(random.uniform(MIN_SCROLL_DELAY, MAX_SCROLL_DELAY))
            scroll_count += 1
        
        print(f"Scraped {len(posts)} posts from feed")
        return posts
    
    def _extract_post_data(self, driver, post_element):
        """
        Extract data from a LinkedIn post element
        
        Args:
            driver: Selenium WebDriver instance
            post_element: The post web element
            
        Returns:
            dict: Post data including author, text, and URLs
        """
        try:
            # Extract post ID
            post_id = post_element.get_attribute("data-urn")
            author_name = "Unknown"
            author_link = ""

            # Extract author info
            try:
                author_container = post_element.find_element(
                    By.CSS_SELECTOR,
                    "a.update-components-actor__meta-link"
                )
                author_link = author_container.get_attribute("href").strip()

                # Try to get the author name
                try:
                    author_name_span = author_container.find_element(
                        By.CSS_SELECTOR,
                        ".update-components-actor__title span span[aria-hidden='true']"
                    )
                    extracted_name = author_name_span.text.strip()
                    if extracted_name:
                        author_name = extracted_name
                except NoSuchElementException:
                    # Fallback: extract name from the profile URL if name is not found
                    if "linkedin.com/in/" in author_link:
                        name_part = author_link.split("linkedin.com/in/")[1].split("?")[0]
                        author_name = name_part.replace("-", " ").title()

            except NoSuchElementException:
                author_name = "Unknown"
                author_link = ""

            # Extract post text
            try:
                text_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2__description")
                post_text = text_element.text.strip()
            except NoSuchElementException:
                # Try alternative selectors for different post types
                try:
                    text_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-text")
                    post_text = text_element.text.strip()
                except NoSuchElementException:
                    post_text = ""

            # Extract post URL
            try:
                post_url_element = post_element.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2__update-link-container a")
                post_url = post_url_element.get_attribute("href")
            except NoSuchElementException:
                # Generate fallback URL based on post ID
                if "activity" in post_id:
                    activity_id = post_id.split(":")[-1]
                    post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}"
                else:
                    post_url = ""

            return {
                "post_id": post_id,
                "author_name": author_name,
                "author_link": author_link,
                "post_text": post_text,
                "post_url": post_url,
                "post_element": post_element  # Keep reference to the actual element for interactions
            }

        except Exception as e:
            print(f"Error extracting data from post: {e}")
            return None
