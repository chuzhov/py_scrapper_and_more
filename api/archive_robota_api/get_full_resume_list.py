from main import logger, session, api_headers

from utils.request_utils import send_request, parse_json_response

# Get full resume list function
def get_full_resume_list():
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

    logger.info("Sending POST request to full resume list API")
    resume_response = send_request("POST", extended_resume_url, headers=api_headers, json_data=request_body)
    
    resume_data = parse_json_response(resume_response)
    if resume_data:
        logger.info(f"POST request to resume API successful! Obtained {len(resume_data['data']['seekerResumes'])} resumes.")
        return resume_data.get("data", {}).get("seekerResumes", [])

    logger.error("Failed to fetch full resume list for no reason.")
    return None
        
                
        