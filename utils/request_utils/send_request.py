import requests

# Utility function to send requests
def send_request(logger, session, method, url, headers=None, data=None, json_data=None):
    try:
        if method == "GET":
            response = session.get(url, headers=headers)
        elif method == "POST":
            response = session.post(url, headers=headers, data=data, json=json_data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code == 200:
            return response
        else:
            logger.error(f"Request to {url} failed with status code: {response.status_code}")
            logger.error(response.text[:500])
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during {method} request to {url}: {e}")
        return None