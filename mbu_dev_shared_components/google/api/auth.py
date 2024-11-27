"""
Google OAuth2 Token Fetcher.
This file contains a generic implementation of a class for
fetching Google OAuth2 tokens using a P12 key file.
"""
import base64
import json
import time
from typing import List, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
import requests


class GoogleTokenFetcher:
    """
    Class for fetching Google OAuth2 tokens using a P12 key file.

    Attributes:
        p12_key_path (str): Path to the P12 key file.
        scopes (List[str]): A list of scopes required for the token.
        app_email (str): Email for the service account.
        admin_email (str): Email for the admin account.
    """

    def __init__(self, p12_key_path: str, scopes: List[str], app_email: str, admin_email: str):
        """
        Initializes GoogleTokenFetcher with necessary attributes.

        Args:
            p12_key_path (str): Path to the P12 key file.
            scopes (List[str]): A list of scopes required for the token.
            app_email (str): Email for the service account.
            admin_email (str): Email for the admin account.
        """
        self.p12_key_path = p12_key_path
        self.scopes = scopes
        self.app_email = app_email
        self.admin_email = admin_email

    @staticmethod
    def _url_encode(data: bytes) -> str:
        """
        URL-encodes a byte sequence in Base64 format.

        Args:
            data (bytes): Data to be URL-encoded.

        Returns:
            str: URL-safe Base64-encoded string.
        """
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    def _load_private_key(self) -> Any:
        """
        Loads the private key from the P12 file.

        Returns:
            Any: The private key object.
        """
        with open(self.p12_key_path, 'rb') as f:
            p12_data = f.read()

        private_key, _, _ = load_key_and_certificates(
            p12_data,
            password=b'notasecret'
        )
        return private_key

    def _create_jwt(self, private_key: Any, now: int, expiry_date: int) -> str:
        """
        Creates a JWT signed with the private key.

        Args:
            private_key (Any): The private key object.
            now (int): The current time in seconds since epoch.
            expiry_date (int): The expiration time of the token in seconds since epoch.

        Returns:
            str: The signed JWT.
        """
        header = {
            "alg": "RS256",
            "typ": "JWT"
        }
        raw_header = self._url_encode(json.dumps(header).encode('utf-8'))

        claims = {
            "iss": self.app_email,
            "sub": self.admin_email,
            "scope": ' '.join(self.scopes),
            "aud": "https://www.googleapis.com/oauth2/v4/token",
            "exp": expiry_date,
            "iat": now
        }
        raw_claims = self._url_encode(json.dumps(claims).encode('utf-8'))

        to_sign = f"{raw_header}.{raw_claims}".encode('utf-8')
        signature = private_key.sign(
            to_sign,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return f"{raw_header}.{raw_claims}.{self._url_encode(signature)}"

    def get_google_token(self) -> Dict[str, Any]:
        """
        Fetches a Google OAuth2 token using the P12 key file.

        Returns:
            Dict[str, Any]: Response data from the token request.
        """
        private_key = self._load_private_key()

        now = int(time.time())
        expiry_date = now + 3600

        jwt = self._create_jwt(private_key, now, expiry_date)

        fields = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': jwt
        }

        response = requests.post(
            "https://www.googleapis.com/oauth2/v4/token",
            data=fields,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=60
        )

        response.raise_for_status()
        return response
