import requests
import json



class Auth:

    def __init__(self, 
                 session, 
                 api_headers,
                 username, password, 
                 touch_url="https://robota.ua/auth/login", 
                 login_url="https://auth-api.robota.ua/Login",
                 logger=None):
        
        self.session = session
        self.logger = logger
        self.api_headers = api_headers
        
        """Initialize Auth class with credentials and URL"""
        self.username = username
        self.password = password
        self.touch_url = touch_url
        self.login_url = login_url

    def _make_get_request(self):
        """Handle initial GET request to retrieve cookies using global session"""
        try:
            
            get_response = self.session.get(self.touch_url, headers=self.api_headers)

            if get_response.status_code == 200:
                self.logger.debug("Touch GET request successful!")
                return True
            else:
                self.logger.error(f"GET request failed with status code: {get_response.status_code}")
                self.logger.error(get_response.text[:500])
                return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during GET request: {e}")
            self.logger.error(f"Request exception during GET: {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return False

    def _make_post_request(self):
        """Handle POST request with login credentials using global session"""
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            post_response = self.session.post(
                self.login_url, 
                headers=self.api_headers,
                data=json.dumps(payload)
            )
            
            if post_response.status_code == 200:
                self.logger.debug("Login successful")
                return post_response
            else:
                self.logger.error(f"POST request failed with status code: {post_response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during POST request: {e}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return None

    def _extract_token(self, post_response):
        """Extract JWT token from cookies or response body"""
        token = self.session.cookies.get("jwt-token", None)
        if token:
            return token

        try:
            post_response_data = post_response.json()
            token = post_response_data.get("token")
            if token:
                return token
            else:
                return None
        except json.JSONDecodeError:
            self.logger.error("Response body is not valid JSON. Cannot proceed to resume API.")
            return None

    def login(self):
        """Perform login and update headers with JWT token"""
        # Step 1: Make GET request
        if not self._make_get_request():
            return False

        # Step 2: Make POST request
        post_response = self._make_post_request()
        if not post_response:
            return False

        # Step 3: Extract token and update global headers
        token = self._extract_token(post_response)
        if token:
            self.api_headers["Authorization"] = f"Bearer {token}"
            self.logger.info("Token extracted successfully")
            return self.api_headers
        return False

