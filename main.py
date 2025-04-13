# main.py
import sys
import time
import random
import argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Import project modules
from config import HEADLESS_MODE, MAX_POSTS_TO_SCRAPE
from core.auth import LinkedInAuth
from core.feed_scrapper import FeedScraper
from core.ai_filter import AIFilter
from core.action_engine import ActionEngine

def setup_driver():
    """Set up and configure the Selenium WebDriver"""
    options = Options()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")  # Add this line to ignore SSL errors
    options.add_argument("--allow-insecure-localhost")  # Allow insecure localhost connections (optional)
    options.add_argument("--incognito")  # Use incognito mode
    # Use webdriver_manager to automatically handle ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(service=service, options=options)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="LinkedIntel - LinkedIn Automation with AI")
    parser.add_argument("--mode", choices=["feed", "connect", "message"], default="feed",
                        help="Operation mode: feed (default), connect, or message")
    parser.add_argument("--posts", type=int, default=MAX_POSTS_TO_SCRAPE,
                        help=f"Maximum number of posts to process (default: {MAX_POSTS_TO_SCRAPE})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze but don't perform any actions")
    
    return parser.parse_args()

def main():
    """Main application entry point"""
    print("Starting LinkedIntel...")
    args = parse_arguments()
    
    try:
        # Initialize WebDriver
        driver = setup_driver()
        
        # Initialize components
        auth = LinkedInAuth()
        feed_scraper = FeedScraper()
        ai_filter = AIFilter()
        action_engine = ActionEngine()
        
        # Login to LinkedIn
        if not auth.login(driver):
            print("Failed to log in to LinkedIn. Exiting.")
            driver.quit()
            return
        
        # Process feed
        if args.mode == "feed":
            process_feed(driver, feed_scraper, ai_filter, action_engine, args.posts, args.dry_run)
        # Add other modes here as they're implemented
        
        # Clean up
        print("Completed successfully!")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        # Always close the driver
        try:
            driver.quit()
        except:
            pass

def process_feed(driver, feed_scraper, ai_filter, action_engine, max_posts=10, dry_run=False):
    """Process LinkedIn feed posts with AI analysis"""
    print(f"Processing feed - will analyze up to {max_posts} posts")
    
    # Scrape feed posts
    posts = feed_scraper.scrape_feed(driver)
    
    # Process each post
    processed_count = 0
    
    for post in posts[:max_posts]:
        post_id = post.get("post_id", "unknown").split(":")[-1]
        author = post.get("author_name", "Unknown")
        
        print(f"\nProcessing post {processed_count + 1}/{max_posts} by {author} (ID: {post_id})")
        
        # Analyze post with AI
        print("Analyzing post with AI...")
        analysis = ai_filter.analyze_post(post)
        
        # Display analysis results
        print(f"Analysis results:")
        print(f"  Should like: {analysis.get('should_like', False)}")
        print(f"  Should comment: {analysis.get('should_comment', False)}")
        if analysis.get('should_comment', False):
            print(f"  Suggested comment: {analysis.get('comment_text', '')[:50]}...")
        print(f"  Reasoning: {analysis.get('reasoning', '')[:100]}...")
        
        # Perform actions if not in dry run mode
        if not dry_run:
            print("Performing actions...")
            results = action_engine.perform_actions(driver, post, analysis)
            
            print(f"Action results:")
            print(f"  Liked: {results.get('liked', False)}")
            print(f"  Commented: {results.get('commented', False)}")
            if results.get("errors"):
                print(f"  Errors: {', '.join(results.get('errors', []))}")
        else:
            print("Dry run mode - no actions performed")
        
        processed_count += 1
        
        # Random delay between posts
        if processed_count < max_posts:
            delay = random.uniform(5, 10)
            print(f"Waiting {delay:.1f} seconds before processing next post...")
            time.sleep(delay)
    
    print(f"\nProcessed {processed_count} posts")

if __name__ == "__main__":
    main()