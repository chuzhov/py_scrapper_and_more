import os
from dotenv import load_dotenv
import requests
import json
from bs4 import BeautifulSoup

# Load the API headers from a separate file
from api.robota_api_headers import api_headers
from api.auth import Auth
from api.robota_api import Robota_API

from api.jinni_api import Jinny_API


# Load environment variables from .env file
load_dotenv()

# Set up logging
from utils.logger import setup_logger
logger = setup_logger("jinny_api")

USERNAME = os.getenv("JINNY_USERNAME")
PASSWORD = os.getenv("JINNY_PASSWORD")


djinny = Jinny_API(username=USERNAME, password=PASSWORD, logger=logger)

djinny.login()
inbox_response = djinny.get_authenticated_page("https://djinni.co/my/inbox/")

print(inbox_response.text[:500]) if inbox_response else print("Failed to retrieve authenticated page")

soup = BeautifulSoup(inbox_response.text, 'html.parser')
print(soup.prettify())