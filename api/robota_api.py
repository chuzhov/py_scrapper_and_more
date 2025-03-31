import requests
import json

class Robota_API:

    def __init__(self, session, api_headers, logger=None):
        self.session = session
        self.api_headers = api_headers
        self.logger = logger
        self.resume_list = []

    def get_all_resume_data(self):
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
            resume_response = self.session.post(extended_resume_url, headers=self.api_headers, json=request_body)
            
            if resume_response.status_code == 200:
                self.logger.debug("POST request to resume API successful!")
                
                # Parse the JSON response
                resume_data = resume_response.json()
                
                # Extract the list of resumes
                self.resume_list = resume_data.get("data", {}).get("seekerResumes", [])
                
                self.logger.info(f"Retrieved {len(self.resume_list)} resumes:")
                for resume in self.resume_list:
                    self.logger.info(f"- ID: {resume['id']}, Title: {resume['title']}, Status: {resume['state']['state']}, Update Date: {resume['updateDate']}")

                return self.resume_list    
            else:
                self.logger.error(f"POST request to resume API failed with status code: {resume_response.status_code}")
                self.logger.error(resume_response.text[:500])

        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during POST request to resume API: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

        return None

    def get_active_resume_id_list(self):
        """Get the list of active resume IDs"""
        return [resume["id"] for resume in self.resume_list if resume["state"]["state"] == "ACTIVE"]
        
    def popup_resume(self, resume_id):
        """Popup a resume by its ID"""
        popup_url = "https://dracula.robota.ua/?=SeekerProfResumePopup"

        # GraphQL mutation to popup a resume
        graphql_mutation = """
        mutation UpdateSeekerProfResumeSortDate($input: UpdateSeekerProfResumeSortDateInput!) {
            updateSeekerProfResumeSortDate(input: $input) {
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
        }
        """

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
            update_response = self.session.post(popup_url, headers=self.api_headers, json=request_body)
            
            if update_response.status_code == 200:
                self.logger.debug(f"POST request to popup resume {resume_id} successful!")
                
                # Parse the JSON response
                update_data = update_response.json()
                
                # Check for errors in the response
                errors = update_data.get("data", {}).get("updateSeekerProfResumeSortDate", {}).get("errors", [])
                if errors:
                    self.logger.error("Errors occurred during the popup:")
                    for error in errors:
                        self.logger.error(f"- {error.get('message', 'Unknown error')} (Type: {error.get('__typename')})")
                else:
                    updated_resume = update_data.get("data", {}).get("updateSeekerProfResumeSortDate", {}).get("profResume", {})
                    self.logger.info(f"Successfully popped up resume with ID: {updated_resume.get('id')}")
                    return updated_resume.get("id")
                    
            else:
                self.logger.error(f"POST request to popup resume failed with status code: {update_response.status_code}")
                self.logger.error(update_response.text[:500])

        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during POST request to popup resume: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

        return None
    
    def get_socket_connection_details(self):
        """Get connection details"""
        connect_url = "https://socket-api.robota.ua/v1/connect"
        
        try:
            connect_response = self.session.get(connect_url, headers=self.api_headers)
            
            if connect_response.status_code == 200:
                self.logger.debug("GET request to connect API successful!")
                return connect_response.json()
            else:
                self.logger.error(f"GET request to connect API failed with status code: {connect_response.status_code}")
                self.logger.error(connect_response.text[:500])

        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during GET request to connect API: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

        return None
    
    def get_short_resume_data(self):
        # URL of the resume API endpoint
        resume_url = "https://ua-api.robota.ua/resume"

        # Send the GET request to the resume API endpoint
        try:
            resume_response = self.session.get(resume_url, headers=self.api_headers)
            
            if resume_response.status_code == 200:
                self.logger.debug("🟢 GET request to resume API successful!")
                # Parse the JSON response

                try:
                    resume_data = resume_response.json()
                except json.JSONDecodeError:
                    self.logger.error("🔴 Failed to decode JSON response from resume API.")
                    exit()     
        
                # Iterate over the list of resumes (if it's a list)
                if isinstance(resume_data, list):
                    return resume_data
                        
                else:
                    self.logger.error("🔴 Unexpected response format from resume API: Expected a list.")
                    
            else:
                self.logger.error(f"GET request to resume API failed with status code: {resume_response.status_code}")
                self.logger.error(resume_response.text[:500])

        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during GET request to resume API: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
        return None
