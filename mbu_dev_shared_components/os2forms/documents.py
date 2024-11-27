"""This module has functions to do with document related calls to the OS2Forms api."""
import requests


def download_file_bytes(url: str, os2_api_key: str) -> bytes:
    """Downloads the content of a file from a specified URL, appending an API key to the URL for authorization.
    The API key is retrieved from an environment variable 'OS2ApiKey'.

    Parameters:
    url (str): The URL from which the file will be downloaded.
    os2_api_key (str): The API-key for OS2Forms api.

    Returns:
    bytes: The content of the file as a byte stream.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {
        'Content-Type': 'application/json',
        'api-key': f'{os2_api_key}'
    }
    response = requests.request(method='GET', url=url, headers=headers, timeout=60)
    response.raise_for_status()

    return response.content
