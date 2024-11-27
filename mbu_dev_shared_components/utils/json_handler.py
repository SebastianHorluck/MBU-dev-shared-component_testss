"""
This module provides a class for manipulating JSON objects by transforming lists
within the JSON into dictionaries with specified keys.

The primary class in this module is JSONManipulator, which contains methods for
converting lists associated with keys in a JSON object into dictionaries. This
is useful for restructuring JSON data into a more readable and accessible format.
"""
import json
from typing import Any, Dict, List, Union


class JSONManipulator:
    """
    A class used to manipulate JSON objects.

    Methods
    -------
    transform_all_lists(json_obj: List[Union[List[Any], Dict[str, Any]]], key_map: List[str]) -> List[Union[Dict[str, Any], Any]]:
        Transforms all lists in the JSON object into dictionaries with specified keys.

    insert_key_value_pairs(json_obj: Union[Dict[str, Any], List], key_value_pairs: Dict[str, Any]) -> Union[Dict[str, Any], List]:
        Inserts key-value pairs into each node of the JSON object, including nested nodes.
    """

    @staticmethod
    def transform_all_lists(json_obj: List[Union[List[Any], Dict[str, Any]]], key_map: List[str]) -> List[Union[Dict[str, Any], Any]]:
        """
        Transforms all lists in the JSON object into dictionaries with specified keys.

        Parameters
        ----------
        json_obj : list
            The JSON object to be manipulated.

        key_map : list
            The list of keys to be used for the new dictionaries.

        Returns
        -------
        list
            The updated JSON object with the transformed key-value pairs for all lists.
        """
        if not isinstance(json_obj, list):
            raise TypeError("The input must be a list.")

        for i, item in enumerate(json_obj):
            if isinstance(item, list):
                if len(item) == len(key_map):
                    json_obj[i] = {key_map[j]: item[j] for j in range(len(key_map))}
                else:
                    raise ValueError(f"The length of the list at index {i} and the key_map must match.")
            elif isinstance(item, dict):
                JSONManipulator.transform_all_lists(list(item.values()), key_map)
        return json_obj

    @staticmethod
    def insert_key_value_pairs(json_obj: Union[str, Dict[str, Any], List], key_value_pairs: Dict[str, Any]) -> Union[Dict[str, Any], List]:
        """
        Inserts key-value pairs into the top level of the JSON object, and nested level if specified.

        Parameters
        ----------
        json_obj : Union[str, Dict[str, Any], List]
            The JSON object to be manipulated, either as a JSON string, a dictionary, or a list.

        key_value_pairs : Dict[str, Any]
            The key-value pairs to be inserted into the JSON object.

        Returns
        -------
        Union[Dict[str, Any], List]
            The updated JSON object with the inserted key-value pairs.
        """
        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

        def insert_pairs(target_obj: Union[Dict[str, Any], List], pairs: Dict[str, Any]):
            if isinstance(target_obj, dict):
                for key, value in pairs.items():
                    target_obj[key] = value
            elif isinstance(target_obj, list):
                for item in target_obj:
                    if isinstance(item, (dict, list)):
                        insert_pairs(item, pairs)
            else:
                raise TypeError("The input must be a dictionary or a list.")

        if isinstance(json_obj, dict):
            for key, value in key_value_pairs.items():
                if isinstance(value, dict) and key in json_obj:
                    insert_pairs(json_obj[key], value)
                else:
                    json_obj[key] = value
        elif isinstance(json_obj, list):
            for item in json_obj:
                if isinstance(item, (dict, list)):
                    JSONManipulator.insert_key_value_pairs(item, key_value_pairs)
        else:
            raise TypeError("The input must be a dictionary or a list.")

        return json_obj
