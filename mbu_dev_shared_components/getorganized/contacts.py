"""This module has functions to do with contact related calls
to the GetOrganized api."""
import requests
from mbu_dev_shared_components.getorganized.auth import get_ntlm_go_api_credentials


def contact_lookup(person_ssn: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Searches for contact information based on the person's Social Security Number (SSN) through a POST request.
    The function constructs the request by encoding the SSN and a fixed field name into the request body.

    Parameters:
    person_ssn (str): The Social Security Number of the person to look up.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.

    Notes:
    The 'ContactDataFieldName' is set to 'CCMContactData' as a fixed query parameter for this particular API endpoint.
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {"Id": person_ssn, "ContactDataFieldName": "CCMContactData"}
    encoded_body = '&'.join([f"{key}={value}" for key, value in body.items()])
    response = requests.request(method='POST', url=api_endpoint, headers=headers, data=encoded_body, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response
