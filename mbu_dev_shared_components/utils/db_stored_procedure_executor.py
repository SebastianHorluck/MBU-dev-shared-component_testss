"""
This module contains a generic function for executing stored procedures in a database
via the pyodbc library. The function connects to the database and executes the stored
procedure with provided parameters, returning the success status and any error messages.
"""
import json
from typing import Dict, Any, Union
from dateutil import parser
import pyodbc


def execute_stored_procedure(connection_string: str, stored_procedure: str, params: Dict[str, Any]) -> Dict[str, Union[bool, str, Any]]:
    """
    Executes a stored procedure with the given parameters.

    Args:
        connection_string (str): The connection string to connect to the database.
        stored_procedure (str): The name of the stored procedure to execute.
        params (Dict[str, Any]): A dictionary of parameters to pass to the stored procedure.
                                 Each value should be a tuple of (type, actual_value).

    Returns:
        Dict[str, Union[bool, str, Any]]: A dictionary containing the success status, an error message (if any),
                                           and additional data.
    """
    result = {
        "success": False,
        "error_message": None,
    }

    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "datetime": parser.isoparse,
        "json": lambda x: json.dumps(x, ensure_ascii=False)
    }

    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                param_placeholders = ', '.join([f"@{key} = ?" for key in params.keys()])
                param_values = []

                for key, value in params.items():
                    if isinstance(value, tuple) and len(value) == 2:
                        value_type, actual_value = value
                        if value_type in type_mapping:
                            param_values.append(type_mapping[value_type](actual_value))
                        else:
                            param_values.append(actual_value)
                    else:
                        raise ValueError("Each parameter value must be a tuple of (type, actual_value).")

                sql = f"EXEC {stored_procedure} {param_placeholders}"
                cursor.execute(sql, tuple(param_values))
                conn.commit()
                result["success"] = True
    except pyodbc.Error as e:
        result["error_message"] = f"Database error: {str(e)}"
    except ValueError as e:
        result["error_message"] = f"Value error: {str(e)}"
    except Exception as e:
        result["error_message"] = f"An unexpected error occurred: {str(e)}"

    return result
