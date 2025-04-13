# core/ai_filter.py
import json
import time
import os
from pathlib import Path
import openai

from config import OPENAI_API_KEY, OPENAI_MODEL, DATA_DIR
from utils.parser import parse_ai_response

# Set OpenAI API key from config
openai.api_key = OPENAI_API_KEY

class AIFilter:
    def __init__(self):
        self.cache_dir = Path(DATA_DIR) / "cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def analyze_post(self, post_data):
        """
        Analyze a LinkedIn post using OpenAI to decide on actions
        
        Args:
            post_data: Dictionary containing post information
            
        Returns:
            dict: Analysis results with action flags and generated content
        """
        post_id = post_data.get("post_id", "").split(":")[-1]
        cache_file = self.cache_dir / f"post_{post_id}.json"
        
        # Check if we have cached results
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Extract relevant data for analysis
        author_name = post_data.get("author_name", "Unknown")
        post_text = post_data.get("post_text", "")
        
        # Skip empty posts
        if not post_text.strip():
            return {
                "should_like": False,
                "should_comment": False,
                "comment_text": "",
                "reasoning": "Post text is empty"
            }
        
        # Prepare prompt for OpenAI
        prompt = self._create_prompt(author_name, post_text)
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that helps decide how to interact with LinkedIn posts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and parse response
            ai_response = response.choices[0].message.content
            analysis_result = parse_ai_response(ai_response)
            
            # Cache the result
            with open(cache_file, 'w') as f:
                json.dump(analysis_result, f)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error analyzing post with OpenAI: {e}")
            return {
                "should_like": False,
                "should_comment": False,
                "comment_text": "",
                "reasoning": f"Error: {str(e)}"
            }
    
    def _create_prompt(self, author_name, post_text):
        """Create a prompt for the OpenAI API"""
        return f"""
You are analyzing a LinkedIn post to decide if and how to interact with it.

POST AUTHOR: {author_name}
POST CONTENT: 
{post_text}

Based on this post, please answer the following questions:

1. Should I like this post? (Yes/No)
2. Should I comment on this post? (Yes/No)
3. If I should comment, what would be a thoughtful, professional comment?
4. What's your reasoning for these decisions?

Format your response exactly like this:
LIKE: Yes/No
COMMENT: Yes/No
COMMENT_TEXT: [Your suggested comment if applicable]
REASONING: [Your reasoning for these decisions]

The comment should be professional, relevant to the post content, and add value to the conversation. It should sound natural and human-written, not generic or bot-like.
"""