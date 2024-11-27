"""
This module provides functions for interacting with the OS2Forms API,
specifically for fetching form data.

Functions:
    get_forms(url: str) -> requests.Response:
        Fetches form data from the OS2Forms API using a specified URL.

Dependencies:
    requests: This module requires the 'requests' library to make HTTP requests.
"""

import requests


def get_form(os2_api_endpoint: str, os2_api_key: str) -> requests.Response:
    """
    Fetches form data from the OS2Forms API.

    This function sends a GET request to the specified URL and returns the response object.
    It raises an HTTPError if the request returns an unsuccessful status code.

    Args:
        url (str): The URL for the OS2 form to be fetched.

    Returns:
        requests.Response: The response object containing the form data.

    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
        requests.exceptions.RequestException: For other types of request exceptions.
    """
    headers = {
        'Content-Type': 'application/json',
        'api-key': f'{os2_api_key}'
        }
    response = requests.get(url=os2_api_endpoint, headers=headers, timeout=60)
    response.raise_for_status()

    return response


def get_list_of_active_forms(os2_api_endpoint: str, data_webform_id: str, os2_api_key: str) -> requests.Response:
    """
    Fetches a list of all active submissions.

    Args:
        data webform id (str): The uniquie id for the webform.
        os2 api key (str): The api-key for OS2Forms API.

    Returns:
        requests.Response: The response object containing the list of submissions.

    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
        requests.exceptions.RequestException: For other types of request exceptions.
    """
    headers = {
        'Content-Type': 'application/json',
        'api-key': f'{os2_api_key}'
        }
    url = f"{os2_api_endpoint}/webform_rest/{data_webform_id}/submissions"
    response = requests.get(url=url, headers=headers, timeout=60)
    response.raise_for_status()

    return response
