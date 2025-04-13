# utils/parser.py
import json

def parse_ai_response(response: str):
    """
    Parses the AI response and extracts the necessary action criteria.
    """
    try:
        # Assuming response is a JSON string with necessary info
        parsed_response = json.loads(response)
        should_like = parsed_response.get('should_like', False)
        should_comment = parsed_response.get('should_comment', False)
        comment_text = parsed_response.get('comment_text', "")
        reasoning = parsed_response.get('reasoning', "")

        return {
            "should_like": should_like,
            "should_comment": should_comment,
            "comment_text": comment_text,
            "reasoning": reasoning
        }
    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        return {}
