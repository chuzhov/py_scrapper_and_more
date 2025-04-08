import os
from dotenv import load_dotenv
import requests
import json
from bs4 import BeautifulSoup

# Load the API headers from a separate file
from api.robota_api_headers import api_headers
from api.auth import Auth
from api.robota_api import Robota_API


# Load environment variables from .env file
load_dotenv()

# Set up logging
from utils.logger import setup_logger
logger = setup_logger("rabota_api")

USERNAME = os.getenv("ROBOTA_USERNAME")
PASSWORD = os.getenv("ROBOTA_PASSWORD")

session = requests.Session()

# Initialize Auth class
robota_auth = Auth(session=session, 
            api_headers=api_headers, 
            username=USERNAME, password=PASSWORD, 
            touch_url="https://robota.ua/auth/login",
            login_url="https://auth-api.robota.ua/Login", 
            logger=logger)
    
# Perform login
api_headers = robota_auth.login()
if not api_headers:
    print("🔴 Login failed. See log for details")
    exit()

print("Login successful!")
robota = Robota_API(session=session, api_headers=api_headers, logger=logger)
# Get all resume data
resume_data = robota.get_all_resume_data()
if not resume_data or len(resume_data) == 0:
    print("No resume data found!")
    exit()
print("Resume data retrieved successfully!")
# Extract active resume IDs
active_ids = robota.get_active_resume_id_list()

# =======================================================================================
# Pop up the resume

for resume_id in active_ids:

    # Pop up the resume
    if robota.popup_resume(resume_id):
        print(f"Resume {resume_id} popped up successfully!")
    else:
        print(f"Failed to pop up resume {resume_id}.")

# =======================================================================================
# Profile page actions


# URL of the profile page
profile_url = "https://robota.ua/my/profile"

# Send the GET request to the profile page using the same session (with authenticated cookies)
try:
    profile_response = session.get(profile_url, headers=api_headers)
    
    if profile_response.status_code == 200:
        print("🟢 GET request to profile page successful!")
    else:
        print(f"🔴 GET request to profile page failed with status code: {profile_response.status_code}")
        print(profile_response.text[:500])
        exit()

except requests.exceptions.RequestException as e:
    print(f"🔴 An error occurred during GET request to profile page: {e}")
    exit()

# Parse the profile page HTML with BeautifulSoup
soup = BeautifulSoup(profile_response.text, 'html.parser')

