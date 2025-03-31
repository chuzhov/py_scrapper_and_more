import json

# Utility function to parse JSON responses
def parse_json_response(logger, response):
    try:
        return response.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response.")
        return None