"""Module that inculdes helper functions for file handling."""
import os


def rename_file(current_path, new_name):
    """
    Renames a file from the given current path to a new name.

    Parameters:
    current_path (str): The full path of the file that you want to rename.
    new_name (str): The new name for the file (without the directory path).

    Returns:
    None
    """
    if not os.path.isfile(current_path):
        print(f"The file '{current_path}' does not exist.")
        return

    directory = os.path.dirname(current_path)

    new_path = os.path.join(directory, new_name)

    try:
        os.rename(current_path, new_path)
        print(f"File renamed to '{new_name}' successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{current_path}' does not exist.")
    except PermissionError:
        print(f"Error: You do not have permission to rename '{current_path}'.")
    except OSError as e:
        print(f"OS error occurred: {e}")
