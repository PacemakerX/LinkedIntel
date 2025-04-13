# config.py
import os
from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
TEMPLATES_DIR = ROOT_DIR / "templates"

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

# Google Gemini Configuration

GEMINI_API_KEY= os.environ.get("GEMINI_API_KEY","")
# Browser settings
HEADLESS_MODE = False  # Set to True to run browser in background

# Action limits (for safety and to avoid being detected as a bot)
MAX_LIKES_PER_DAY = 20
MAX_COMMENTS_PER_DAY = 10
MAX_CONNECTION_REQUESTS_PER_DAY = 15
MAX_MESSAGES_PER_DAY = 10

# Delay settings (in seconds)
MIN_ACTION_DELAY = 1.5
MAX_ACTION_DELAY = 4.5
MIN_SCROLL_DELAY = 1.0
MAX_SCROLL_DELAY = 3.0

# Feed scraping settings
MAX_POSTS_TO_SCRAPE = 2
MAX_SCROLL_ITERATIONS = 10