"""
This module defines a Sharepoint class that facilitates interactions with a SharePoint site.
It provides methods for authenticating with the site, listing files in a specified document
library folder, downloading files, and saving them to a local directory. The class is designed
to encapsulate all necessary functionalities for handling files on a SharePoint site, making it
suitable for scripts or applications that require automated access to SharePoint resources.

The Sharepoint class uses the SharePlum library to communicate with SharePoint, handling common
tasks such as authentication, file retrieval, and file management. This includes methods to
authenticate users, fetch file lists from specific library folders, download individual files,
and save them locally. The class is initialized with user credentials and site details, which
are used throughout the class to manage SharePoint interactions.

Usage:
    After creating an instance of the Sharepoint class with the necessary credentials and site details,
    users can call methods to list files in a folder, download a specific file, or retrieve and save
    all files from a folder to a local directory. This makes it easy to integrate SharePoint file
    management into automated workflows or systems.

Example:
    sharepoint_details = {
        "username": "john@do.e",
        "password": "johndoe",
        "site_url": "https://site_url",
        "site_name": "department123",
        "document_library": "Shared documents"
    }
    sp = Sharepoint(**sharepoint_details)
    sp.download_files("FolderName", "C:\\LocalPath")
"""

from pathlib import PurePath
from typing import Optional, List
import os
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext


class Sharepoint:
    """
    A class to interact with a SharePoint site, enabling authentication, file listing,
    downloading, uploading, and saving functionalities within a specified SharePoint document library.

    Attributes:
        username (str): Username for authentication.
        password (str): Password for authentication.
        site_url (str): URL of the SharePoint site.
        site_name (str): Name of the SharePoint site.
        document_library (str): Document library path.
    """

    def __init__(
        self, username: str, password: str, site_url: str, site_name: str, document_library: str
    ):
        """Initializes the Sharepoint class with credentials and site details."""
        self.username = username
        self.password = password
        self.site_url = site_url
        self.site_name = site_name
        self.document_library = document_library
        self.ctx = self._auth()

    def _auth(self) -> Optional[ClientContext]:
        """
        Authenticates to the SharePoint site and returns the client context.

        Returns:
            Optional[ClientContext]: A ClientContext object for interacting with the SharePoint site if authentication is successful,
                            otherwise None.
        """
        try:
            site_full_url = f"{self.site_url}/teams/{self.site_name}"
            ctx = ClientContext(site_full_url).with_credentials(
                UserCredential(self.username, self.password)
            )
            return ctx
        except Exception as e:
            print(f"Failed to authenticate: {e}")
            return None

    def fetch_files_list(self, folder_name: str) -> Optional[List[dict]]:
        """
        Retrieves a list of files from a specified folder within the document library.

        Args:
            folder_name (str): The name of the folder within the document library.

        Returns:
            list: A list of file dictionaries in the specified folder, or None if an error occurs or if the site is not authenticated.
        """
        if self.ctx:
            try:
                folder_url = f"/teams/{self.site_name}/{self.document_library}/{folder_name}"
                folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
                files = folder.files
                self.ctx.load(files)
                self.ctx.execute_query()
                files_list = [{"Name": file.name} for file in files]
                return files_list
            except Exception as e:
                print(f"Error retrieving files: {e}")
                return None
        return None

    def fetch_file_content(self, file_name: str, folder_name: str) -> Optional[bytes]:
        """
        Downloads a file from a specified folder within the document library.

        Args:
            file_name (str): The name of the file to be downloaded.
            folder_name (str): The name of the folder where the file is located.

        Returns:
            Optional[bytes]: The binary content of the file if successful, otherwise None.
        """
        if self.ctx:
            try:
                file_url = f"/teams/{self.site_name}/{self.document_library}/{folder_name}/{file_name}"
                file = self.ctx.web.get_file_by_server_relative_url(file_url)
                file_content = file.read().execute_query()
                return file_content.value
            except Exception as e:
                print(f"Failed to download file: {e}")
                return None
        return None

    def _write_file(self, folder_destination: str, file_name: str, file_content: bytes):
        """
        Saves the binary content of a file to a specified local destination.

        Args:
            folder_destination (str): The local folder path where the file will be saved.
            file_name (str): The name of the file to be saved.
            file_content (bytes): The binary content of the file.
        """
        file_directory_path = PurePath(folder_destination, file_name)
        with open(file_directory_path, "wb") as file:
            file.write(file_content)

    def download_file(self, folder: str, filename: str, folder_destination: str):
        """
        Downloads a specified file from a specified folder and saves it to a local destination.

        Args:
            folder (str): The name of the folder in the document library containing the file.
            filename (str): The name of the file to download.
            folder_destination (str): The local folder path where the downloaded file will be saved.
        """
        file_content = self.fetch_file_content(filename, folder)
        if file_content:
            self._write_file(folder_destination, filename, file_content)
        else:
            print(f"Failed to download {filename}")

    def download_files(self, folder: str, folder_destination: str):
        """
        Downloads all files from a specified folder and saves them to a local destination.

        Args:
            folder (str): The name of the folder in the document library containing the files.
            folder_destination (str): The local folder path where the downloaded files will be saved.
        """
        files_list = self.fetch_files_list(folder)
        if files_list:
            for file in files_list:
                file_content = self.fetch_file_content(file["Name"], folder)
                if file_content:
                    self._write_file(folder_destination, file["Name"], file_content)
                else:
                    print(f"Failed to download {file['Name']}")
        else:
            print(f"No files found in folder {folder}")

    def upload_file(self, folder_name: str, file_path: str, file_name: Optional[str] = None):
        """
        Uploads a single file to a specified folder within the document library.

        Args:
            folder_name (str): The name of the folder within the document library.
            file_path (str): The local path to the file to be uploaded.
            file_name (Optional[str]): The name to give the file in SharePoint. If not provided, uses the name from file_path.
        """
        if self.ctx:
            try:
                if file_name is None:
                    file_name = os.path.basename(file_path)

                folder_url = f"/teams/{self.site_name}/{self.document_library}/{folder_name}"
                target_folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)

                with open(file_path, 'rb') as content_file:
                    file_content = content_file.read()

                target_folder.upload_file(file_name, file_content).execute_query()
                print(f"File '{file_name}' uploaded successfully to '{folder_url}'.")
            except Exception as e:
                print(f"Failed to upload file '{file_name}': {e}")

    def upload_files(self, folder_name: str, files: List[str]):
        """
        Uploads multiple files to a specified folder within the document library.

        Args:
            folder_name (str): The name of the folder within the document library.
            files (List[str]): A list of local file paths to be uploaded.
        """
        if self.ctx:
            for file_path in files:
                try:
                    file_name = os.path.basename(file_path)
                    self.upload_file(folder_name, file_path, file_name)
                except Exception as e:
                    print(f"Failed to upload file '{file_path}': {e}")
