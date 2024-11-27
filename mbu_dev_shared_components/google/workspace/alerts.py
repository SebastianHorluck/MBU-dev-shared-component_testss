"""
This module provides a function to fetch alerts from the Google Alert Center
API with pagination support. The `get_alerts` function sends a GET request
to the Google Alert Center API to retrieve alerts based on the provided access
token and optional filter, handling paginated results.
"""
from typing import Optional, List, Dict
import requests


def get_alerts(access_token: str, alert_filter: Optional[str] = None) -> List[Dict]:
    """
    Fetch alerts from the Google Alert Center API, handling paginated results.

    Args:
        access_token (str): The OAuth 2.0 token for authentication.
        alert_filter (Optional[str], optional): The filter to apply to the alerts query. Defaults to None.

    Returns:
        List[Dict]: A list of alerts data.

    Raises:
        requests.RequestException: If an error occurs during the HTTP request.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Scope": "https://www.googleapis.com/auth/apps.alerts"
    }

    url = 'https://alertcenter.googleapis.com/v1beta1/alerts'
    if alert_filter:
        url += f'?filter={alert_filter}'

    alerts = []
    next_page_token = None

    while True:
        if next_page_token:
            current_url = f'{url}&pageToken={next_page_token}'
        else:
            current_url = url

        response = requests.get(current_url, headers=headers, timeout=60)
        response.raise_for_status()

        data = response.json()
        alerts.extend(data.get('alerts', []))

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return alerts
