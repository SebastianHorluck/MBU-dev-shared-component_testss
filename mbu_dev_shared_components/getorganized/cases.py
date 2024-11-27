"""This module has functions to do with case related calls
to the GetOrganized api."""
import requests
from mbu_dev_shared_components.getorganized.auth import get_ntlm_go_api_credentials


def find_case_by_case_properties(case_data: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Sends a POST request to search for cases based on specific case properties provided in `case_data`.

    Parameters:
    case_data (str): A JSON string containing case properties to filter cases by in the API search.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=case_data, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response


def create_case_folder(case_data: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Sends a POST request to create a new case folder with the provided `case_data`.

    Parameters:
    case_data (str): A JSON string containing the data required to create a new case folder.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=case_data, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response


def create_case(case_data: str, api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Sends a POST request to create a new case in the system with the specified `case_data`.

    Parameters:
    case_data (str): A JSON string containing the data required to create a new case.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=case_data, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response
