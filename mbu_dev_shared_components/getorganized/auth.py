"""This module contains functionality to authenticate against the GetOrganized api."""
from requests_ntlm import HttpNtlmAuth


def get_ntlm_go_api_credentials(api_username: str, api_password: str):
    """Retrieves NTLM authentication credentials for API access.
    This function constructs an authentication object suitable for making NTLM authenticated HTTP requests.

    Returns:
    HttpNtlmAuth: An authentication object configured with the NTLM credentials.

    Parameters:
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Raises:
    KeyError: If the username or password for the GetOrganized are not given.
    """
    ntlm_creds = HttpNtlmAuth(api_username, api_password)

    return ntlm_creds
