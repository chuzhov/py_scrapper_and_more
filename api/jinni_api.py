# popup_profile_url = https://djinni.co/ajax/reactivate/
# method = POST
# headers = api_headers

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError
import logging
from typing import Optional, Dict

from api.jinni_api_headers import jinny_headers

class Jinny_API:
    """API client for interacting with Djinni.co"""

    DEFAULT_HEADERS = {
        **jinny_headers,
    }

    def __init__(
        self,
        username: str,
        password: str,
        touch_url: str = "https://djinni.co/",
        login_url: str = "https://djinni.co/login?from=frontpage_main",
        logger: Optional[logging.Logger] = None,
        timeout: int = 10,
    ):
        """Initialize the API client with credentials and configuration."""
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.touch_url = touch_url
        self.login_url = login_url
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.headers = self.DEFAULT_HEADERS.copy()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging if not provided."""
        if not self.logger.handlers:
            logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
            self.logger.debug("Logging configured for JinnyAPI")

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Generic request handler with error handling."""
        self.logger.info(f"Making {method} request to {url}")
        try:
            response = self.session.request(
                method,
                url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
            self.logger.info(f"{method} request to {url} successful. Status code: {response.status_code}")
            return response
        except Timeout:
            self.logger.error(f"Timeout after {self.timeout}s for {method} request to {url}")
            return None
        except ConnectionError:
            self.logger.error(f"Connection error for {method} request to {url}")
            return None
        except RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error for {method} request to {url}: {str(e)}")
            return None

    def _extract_csrf_token(self, response: requests.Response) -> Optional[str]:
        """Extract CSRF token from login page response."""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if not csrf_input or 'value' not in csrf_input.attrs:
                self.logger.error("CSRF token not found in login page")
                return None
            token = csrf_input['value']
            self.logger.debug(f"Extracted CSRF token: {token[:10]}...")  # Log partial token for security
            return token
        except Exception as e:
            self.logger.error(f"Failed to parse CSRF token: {str(e)}")
            return None

    def _touch_site(self) -> bool:
        """Simulate initial site visit to gather cookies."""
        response = self._make_request("GET", self.touch_url)
        return bool(response)

    def _get_login_page(self) -> Optional[requests.Response]:
        """Fetch login page to extract CSRF token."""
        return self._make_request("GET", self.login_url)

    def _login_post(self, csrf_token: str) -> Optional[requests.Response]:
        """Perform login POST request."""
        payload = {
            "email": self.username,
            "password": self.password,
            "csrfmiddlewaretoken": csrf_token,
        }
        self.headers.update({
            "Origin": "https://djinni.co",
            "Referer": self.login_url,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        
        response = self._make_request(
            "POST",
            self.login_url,
            data=payload,  # Form-encoded data
            allow_redirects=True
        )
        
        if response and response.status_code == 200:
            self.logger.info(f"Login successful! Final URL: {response.url}")
            return response
        self.logger.error(f"Login failed. Final URL: {response.url if response else 'None'}")
        return None

    def login(self) -> bool:
        """Perform complete login sequence."""
        self.logger.info(f"Starting login process on behalf of {self.username}")

        # Step 1: Touch site to gather initial cookies
        if not self._touch_site():
            self.logger.error("Failed to touch site. Aborting login.")
            return False

        # Step 2: Get login page and extract CSRF token
        login_page_resp = self._get_login_page()
        if not login_page_resp:
            self.logger.error("Failed to fetch login page. Aborting login.")
            return False

        csrf_token = self._extract_csrf_token(login_page_resp)
        if not csrf_token:
            self.logger.error("Failed to extract CSRF token. Aborting login.")
            return False

        # Step 3: Perform login POST
        post_response = self._login_post(csrf_token)
        if not post_response:
            self.logger.error("Login POST request failed.")
            return False
        self.logger.info("Login POST request successful.")
        return True

    def get_authenticated_page(self, url: str) -> Optional[requests.Response]:
        """Fetch a page using the authenticated session."""
        response = self._make_request("GET", url)
        return response if response else None
