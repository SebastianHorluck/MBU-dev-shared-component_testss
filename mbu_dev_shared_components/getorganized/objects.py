"""
This module contains classes relating data to be used in API requests to
GetOrganized when working with cases and documents.
"""
import dataclasses
from typing import Literal


CaseTypePrefix = Literal["BOR", "EMN", "PPR", "AKT", "ELM", "PER", "GEO", "SAM", "MOD"]


class CaseDataJson:
    """
    A class responsible for creating JSON representations of case data structures for different types of cases.

    This class provides a method to serialize case data into a JSON format.
    """
    def case_data_json(self, case_type_prefix: CaseTypePrefix, metadata_xml: str, return_when_case_fully_created: bool) -> str:
        """
        Creates a JSON string representing a case with the provided attributes.

        Parameters:
        case_type_prefix (CaseTypePrefix): The prefix indicating the type of the case. Must be one of the predefined literal values.
        metadata_xml (str): XML-formatted string containing metadata associated with the case.
        return_when_case_fully_created (bool): A flag indicating whether to wait for the case to be fully created before returning.

        Returns:
        dict: A dictionary representing the case data in JSON format.
        """
        case_data = {
            "CaseTypePrefix": case_type_prefix,
            "MetadataXml": metadata_xml,
            "ReturnWhenCaseFullyCreated": return_when_case_fully_created
        }
        return case_data

    def search_case_folder_data_json(self, case_type_prefix: CaseTypePrefix, person_full_name: str, person_id: str, person_ssn: str) -> str:
        """
        Creates a JSON string representing a search string for case folder with the provided attributes.

        Parameters:
        case_type_prefix (CaseTypePrefix): The prefix indicating the type of the case. Must be one of the predefined literal values.
        person_full_name (str): The full name of the person associated with the case.
        person_id (str): The ID of the person associated with the case.
        person_ssn (str): The Social Security Number of the person associated with the case.

        Returns:
        dict: A dictionary representing the search criteria for the case folder in JSON format.
        """
        search_case_folder_data = {
            "FieldProperties": [
                {
                    "InternalName": "ows_CCMContactData",
                    "Value": f"{person_full_name};#{person_id};#{person_ssn};#;#",
                    "DataType": "Text",
                    "ComparisonType": "Equal",
                    "IsMultiValue": "False"
                },
                {
                    "InternalName": "ows_CaseCategory",
                    "Value": "Borgermappe",
                    "DataType": "Text",
                    "ComparisonType": "Equal",
                    "IsMultiValue": "False"
                }
            ],
            "CaseTypePrefixes": [
                f"{case_type_prefix}"
            ],
            "LogicalOperator": "AND",
            "ExcludeDeletedCases": "True",
            "ReturnCasesNumber": "1"
            }
        return search_case_folder_data


@dataclasses.dataclass
class DocumentJsonCreator:
    """
    A class responsible for creating JSON representations of document data structures
    associated with a specific case.

    This class is used to serialize document attributes into a JSON format.
    """
    def document_data_json(self, case_id: str, list_name: str, folder_path: str, filename: str, metadata: str, overwrite: bool, data_in_bytes: bytes) -> str:
        """
        Creates a JSON string representing a document with the provided attributes.

        Parameters:
        case_id (str): The unique identifier of the case to which the document is related.
        list_name (str): The name of the list within the case where the document is stored.
        folder_path (str): The directory path where the document is located on the case.
        filename (str): The name of the file including its extension.
        metadata (str): XML-formatted string containing metadata associated with the document.
        overwrite (bool): A flag indicating whether the existing file should be overwritten if it exists.
        data_in_bytes (bytes): The binary data of the file being represented.

        Returns:
        dict: A dictionary representing the document data in JSON format.
        """
        document_data = {
            "CaseId": case_id,
            "ListName": list_name,
            "FolderPath": folder_path,
            "FileName": filename,
            "Metadata": metadata,
            "Overwrite": overwrite,
            "Bytes": data_in_bytes
        }
        return document_data
