import shutil
import subprocess
import os
import re


def get_sap_sid():
    """
    Fetches the SAP System ID (SID) dynamically by running shell commands.

    Returns:
    tuple: The SAP SID in uppercase and lowercase or (None, None) if not found.
    """
    try:
        # Execute shell commands to get the SID
        result = subprocess.run('ls /sapmnt', shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        sid = result.stdout.strip()

        # Convert SID to lowercase
        sid_lower = sid.lower()

        # Returns a tuple with the SID in both uppercase and lowercase formats.
        return sid.upper(), sid_lower

    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to fetch SID. Details: {e}")
        return None, None


def backup_file(file_path):
    """
    Creates a backup of the specified file.

    Parameters:
    file_path (str): The path to the file to backup.
    """
    backup_path = f"{file_path}_PRE_SCRIPT.PFL"
    try:
        shutil.copy(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist. Backup failed.")
    except IOError as e:
        print(f"Error: Could not create backup. Details: {e}")


def delete_lines_with_specific_patterns(file_path, patterns_to_delete):
    """
    Deletes lines from a file that contain specific patterns using regular expressions.

    Parameters:
    file_path (str): The path to the file.
    patterns_to_delete (list): List of patterns to delete if they appear alone on a line.
    """
    try:
        # Read the file and process lines
        with open(file_path, 'r') as file:
            lines = file.readlines()
        """
        Compile patterns into regex objects, so now variable regex pattern will include all the 4 patterns compiled into a format that can be used for matching against text.
        
        print("Compiled regex patterns:")
        for pattern in regex_patterns:
        print(pattern)
        
        Compiled regex patterns:
        re.compile('^[0-9]')
        re.compile('^[a-zA-Z].*=$')
        re.compile('^[a-zA-Z][^=]*$')
        re.compile('^[^a-zA-Z0-9#_].*')
        """
        regex_patterns = [re.compile(pattern) for pattern in patterns_to_delete]

        # Filter lines that do not match any of the patterns
        """
        Compiling Patterns:

        The regex_patterns variable stores a list of compiled regex objects. Each object represents one of the patterns you want to match.
        This compilation step converts the string patterns into regex objects that can be used for efficient pattern matching.
        Processing the File:
        
        The script reads the file and processes each line.
        For each line, it checks whether the line matches any of the patterns in regex_patterns.
        If a line matches any of the patterns, it is excluded from being written back to the file.
        Altering the File:
        
        After determining which lines do not match any of the patterns, the file is rewritten, excluding the matched lines.
        This way, the file is effectively modified to remove lines that match any of the patterns without rewriting the entire content from scratch.
        """
        with open(file_path, 'w') as file:
            for line in lines:
                if not any(pattern.match(line.strip()) for pattern in regex_patterns):
                    file.write(line)

        print(f"Lines containing patterns {patterns_to_delete} have been deleted from '{file_path}'.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except IOError as e:
        print(f"Error: Could not write to file. Details: {e}")


if __name__ == "__main__":
    sid, sid_lower = get_sap_sid()

    if sid:
        file_paths = [
            f"/sapmnt/{sid}/profile/{sid}_D00_vhibr{sid_lower}ci",
            f"/sapmnt/{sid}/profile/{sid}_D00_vhibr{sid_lower}ai01",
            f"/sapmnt/{sid}/profile/DEFAULT.PFL"
        ]

        # Updated patterns to delete
        patterns_to_delete = [
            "^[0-9]",  # Lines starting with a digit
            "^[a-zA-Z].*=$",  # Lines starting with a letter and ending with '='
            "^[a-zA-Z][^=]*$",  # Lines starting with a letter and not containing '='
            "^[^a-zA-Z0-9#_].*"  # Lines starting with a special character
        ]

        for file_path in file_paths:
            if os.path.exists(file_path):
                # Create a backup of the file
                backup_file(file_path)

                # Call the function to delete lines containing only the specified patterns
                delete_lines_with_specific_patterns(file_path, patterns_to_delete)
            else:
                print(f"File '{file_path}' does not exist. No actions performed.")
