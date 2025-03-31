import os
from dotenv import load_dotenv
import requests
import json
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Set up logging
from utils.logger import setup_logger
logger = setup_logger()

USERNAME = os.getenv("ROBOTA_USERNAME")
PASSWORD = os.getenv("ROBOTA_PASSWORD")

session = requests.Session()

# Login
login_url = "https://auth-api.robota.ua/Login"
login_data = {
    "email": USERNAME,
    "password": PASSWORD
}

# Create a session to persist cookies across requests
session = requests.Session()

# URL of the login page
url = "https://robota.ua/auth/login"

# Headers for the GET request (from your previous screenshot)
get_headers = {
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,uk;q=0.8,ru;q=0.7,en-GB;q=0.6",
    "Cache-Control": "max-age=0",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Chromium";v="134", "Not-A.Brand";v="24", "Microsoft Edge";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
}

# Send the GET request to retrieve cookies
try:
    get_response = session.get(url, headers=get_headers)
    if get_response.status_code == 200:
        print("🟢 GET request successful!")
        print("Cookies set by the server:", session.cookies.get_dict())
    else:
        print(f"GET request failed with status code: {get_response.status_code}")
        print(get_response.text[:500])
        exit()

except requests.exceptions.RequestException as e:
    print(f"An error occurred during GET request: {e}")
    exit()

# Headers for the POST request (from the new screenshot)
api_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,uk;q=0.8,ru;q=0.7,en-GB;q=0.6",
    "Content-Type": "application/json",
    "Origin": "https://robota.ua",
    "Priority": "u=1, i",
    "Referer": "https://robota.ua/",
    "Sec-Ch-Ua": '"Chromium";v="134", "Not-A.Brand";v="24", "Microsoft Edge";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
}

# Define the login credentials (replace with your actual email and password)
payload = {
    "username": USERNAME,
    "password": PASSWORD
}

# Send the POST request with the credentials
try:
    post_response = session.post(login_url, headers=api_headers, data=json.dumps(payload))
    
    # Check if the request was successful
    if post_response.status_code == 200:
        print("🟢 POST request successful!")
        
    else:
        print(f"POST request failed with status code: {post_response.status_code}")
        

except requests.exceptions.RequestException as e:
    print(f"An error occurred during POST request: {e}")



# Extract the Bearer token from the cookies
token = session.cookies.get("jwt-token")
if token:
    print("Bearer token found in cookies:", token)
else:
    print("No jwt-token cookie found. Checking response body...")
    try:
        post_response_data = post_response.json()
        token = post_response_data.get("token")
        if token:
            print("Bearer token found in response body:", token)
        else:
            print("No token found in response body either. Cannot proceed to resume API.")
            exit()
    except json.JSONDecodeError:
        print("Response body is not valid JSON. Cannot proceed to resume API.")
        exit()

# Add the Authorization header to the API headers
api_headers["Authorization"] = f"Bearer {token}"

# =======================================================================================

connect_url = "https://socket-api.robota.ua/v1/connect"
connect_response = session.get(connect_url, headers=api_headers)
if connect_response.status_code == 200:
    print("🟢 GET request to connect API successful!")
    new_token = connect_response.json().get("token", None)
    if new_token and new_token != token:
        print("New token received")
        token = new_token
        api_headers["Authorization"] = f"Bearer {token}"
else:
    print(f"🔴 GET request to connect API failed with status code: {connect_response.status_code}")


# =======================================================================================

# URL of the resume API endpoint
resume_url = "https://ua-api.robota.ua/resume"

# Send the GET request to the resume API endpoint
try:
    resume_response = session.get(resume_url, headers=api_headers)
    
    if resume_response.status_code == 200:
        print("🟢 GET request to resume API successful!")
        # Parse the JSON response

        try:
            resume_data = resume_response.json()
        except json.JSONDecodeError:
            print("🔴 Failed to decode JSON response from resume API.")
            exit()
        if len(resume_data) == 0:
            print("No resume data found.")
            exit()
   
        # Iterate over the list of resumes (if it's a list)
        if isinstance(resume_data, list):
            for index, resume in enumerate(resume_data, start=1):
                print(f"{index}:", resume)
                
        else:
            print("Resume data is not a list:", resume_data)
            exit()
            
    else:
        print(f"GET request to resume API failed with status code: {resume_response.status_code}")
        print(resume_response.text[:500])
        exit()

except requests.exceptions.RequestException as e:
    print(f"An error occurred during GET request to resume API: {e}")
    exit()


# =======================================================================================
# Get extended list of resumes

extended_resume_url = "https://dracula.robota.ua/?=SeekerResumes"

# GraphQL query to fetch all resumes, matching the browser's query
graphql_query = """
query SeekerResumes {
  seekerResumes {
    ...SeekerResumesInfo
    __typename
  }
}

fragment SeekerResumesInfo on ProfResume {
  similarVacanciesCount
  personal {
    photoUrl
    __typename
  }
  city {
    id
    __typename
  }
  id
  resumeFilling {
    percentage
    __typename
  }
  title
  views {
    totalCount
    __typename
  }
  updateDate
  state {
    ...ResumeState
    __typename
  }
  __typename
}

fragment ResumeState on ResumeState {
  state
  availabilityState
  isAnonymous
  privacySettings {
    hasHiddenPhones
    __typename
  }
  isBannedByModerator
  hiddenCompanies {
    name
    __typename
  }
  __typename
}
"""

# Prepare the request body
request_body = {
    "operationName": "SeekerResumes",
    "variables": {},
    "query": graphql_query
}

# Send the POST request to the resume API endpoint
try:
    resume_response = session.post(extended_resume_url, headers=api_headers, json=request_body)
    
    if resume_response.status_code == 200:
        print("🟢 POST request to resume API successful!")
        
        # Parse the JSON response
        resume_data = resume_response.json()
        
        # Extract the list of resumes
        resumes = resume_data.get("data", {}).get("seekerResumes", [])
        
        print(f"Retrieved {len(resumes)} resumes:")
        for resume in resumes:
            print(f"- ID: {resume['id']}, Title: {resume['title']}, Status: {resume['state']['state']}, Update Date: {resume['updateDate']}")
            
    else:
        print(f"🔴 POST request to resume API failed with status code: {resume_response.status_code}")
        print(resume_response.text[:500])

except requests.exceptions.RequestException as e:
    print(f"An error occurred during POST request to resume API: {e}")

# Filter the list of resumes to only include active resumes
active_ids = [resume['id'] for resume in resumes if resume['state']['state'] == 'ACTIVE']

# =======================================================================================
# Pop up the resume

update_url = 'https://dracula.robota.ua/?q=UpdateSeekerProfResumeSortDate'

# GraphQL mutation to update the sort date of a resume
graphql_mutation = """
mutation UpdateSeekerProfResumeSortDate($input: UpdateSeekerProfResumeSortDateInput!) {
  updateSeekerProfResumeSortDate(input: $input) {
    ...UpdateSeekerProfResume
    __typename
  }
}

fragment UpdateSeekerProfResume on UpdateSeekerProfResumeSortDateOutput {
  profResume {
    id
    __typename
  }
  errors {
    ... on ProfResumeDoesNotExist {
      message
      __typename
    }
    ... on ProfResumeDoesNotBelongToSeeker {
      message
      __typename
    }
    __typename
  }
  __typename
}
"""

for resume_id in active_ids:

    # Prepare the request body
    request_body = {
        "operationName": "UpdateSeekerProfResumeSortDate",
        "variables": {
            "input": {
                "resumeId": resume_id
            }
        },
        "query": graphql_mutation
    }

    # Send the POST request to update the resume sort date
    try:
        update_response = session.post(update_url, headers=api_headers, json=request_body)
        
        if update_response.status_code == 200:
            print(f"🟢 POST request to update resume {resume_id} sort date successful!")
            
            # Parse the JSON response
            update_data = update_response.json()
            
            # Check for errors in the response
            errors = update_data.get("data", {}).get("updateSeekerProfResumeSortDate", {}).get("errors", [])
            if errors:
                print("Errors occurred during the update:")
                for error in errors:
                    print(f"- {error.get('message', 'Unknown error')} (Type: {error.get('__typename')})")
            else:
                updated_resume = update_data.get("data", {}).get("updateSeekerProfResumeSortDate", {}).get("profResume", {})
                print(f"Successfully updated resume with ID: {updated_resume.get('id')}")
                
        else:
            print(f"POST request to update resume sort date failed with status code: {update_response.status_code}")
            print(update_response.text[:500])

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during POST request to update resume sort date: {e}")


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


# # Perform the login
# response = session.post(login_url, json=login_data, headers=headers)
# if "auth/login" in response.url:
#     raise Exception(f"Login failed: {response.status_code} - {response.text}")

# # Check if login was successful
# print('Login status: ', response.status_code)

# # Profile actions
# profile_url = "https://robota.ua/my/profile"
# response = session.get(profile_url, headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')

# # Check profile name
# profile_name_div = soup.find("div", class_="profile-name")
# if profile_name_div and profile_name_div.text.strip() == USERNAME:
#     print('Profile name matches USERNAME')
# else:
#     print("can't find profile name")

# # Click on all buttons with text "Підняти в пошуку"
# buttons = soup.find_all("button", text=lambda t: t and "Підняти в пошуку" in t)
# for button in buttons:
#     form_id = button.find_previous("form")["id"]
#     submit_url = f"https://robota.ua/some-api-endpoint/{form_id}"
#     session.post(submit_url, headers=headers)
#     print('Clicked "Підняти в пошуку" button')