import json
import re

def parse_ai_response(response: str):
    """
    Parses the AI response and extracts the necessary action criteria.
    The response format is structured text, not JSON.
    """
    try:
        # Use regex to extract the necessary fields
        like_match = re.search(r"LIKE: (Yes|No)", response)
        comment_match = re.search(r"COMMENT: (Yes|No)", response)
        comment_text_match = re.search(r"COMMENT_TEXT: (.*)", response)
        reasoning_match = re.search(r"REASONING: (.*)", response)

        # Extract the values or set default values if not found
        should_like = like_match.group(1) if like_match else "No"
        should_comment = comment_match.group(1) if comment_match else "No"
        comment_text = comment_text_match.group(1).strip() if comment_text_match else ""
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"

        # Return the structured dictionary
        return {
            "should_like": should_like,
            "should_comment": should_comment,
            "comment_text": comment_text,
            "reasoning": reasoning
        }

    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        return {
            "should_like": "No",
            "should_comment": "No",
            "comment_text": "",
            "reasoning": "Error: Unable to parse the response."
        }
