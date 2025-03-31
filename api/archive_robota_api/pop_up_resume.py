from main import logger, api_headers
from utils.request_utils import send_request, parse_json_response

def pop_up_resume(resume_id):
    update_url = "https://dracula.robota.ua/?q=UpdateSeekerProfResumeSortDate"
    graphql_mutation = """
    mutation UpdateSeekerProfResumeSortDate($input: UpdateSeekerProfResumeSortDateInput!) {
      updateSeekerProfResumeSortDate(input: $input) {
        profResume {
          id
        }
        errors {
          message
        }
      }
    }
    """
    request_body = {
        "operationName": "UpdateSeekerProfResumeSortDate",
        "variables": {"input": {"resumeId": resume_id}},
        "query": graphql_mutation
    }
    response = send_request("POST", update_url, headers=api_headers, json_data=request_body)
    if response:
        update_data = parse_json_response(response)
        errors = update_data.get("data", {}).get("updateSeekerProfResumeSortDate", {}).get("errors", [])
        if errors:
            logger.error(f"Errors occurred while updating resume {resume_id}: {errors}")
            return False
        else:
            logger.info(f"Successfully updated resume {resume_id}.")
            return True
    
    logger.error(f"Failed to update resume {resume_id}.")
    return False