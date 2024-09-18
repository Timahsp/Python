import shutil
import subprocess
import os
import re


def get_sap_sid():
    try:
        result = subprocess.run('ls /sapmnt', shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        sid = result.stdout.strip()
        sid_lower = sid.lower()
        return sid.upper(), sid_lower

    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to fetch SID. Details: {e}")
        return None, None

def backup_file(file_path):
    backup_path = f"{file_path}_PRE_SCRIPT.PFL"
    try:
        shutil.copy(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist. Backup failed.")
    except IOError as e:
        print(f"Error: Could not create backup. Details: {e}")


def delete_lines_with_specific_patterns(file_path, patterns_to_delete):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        regex_patterns = [re.compile(pattern) for pattern in patterns_to_delete]

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
        file_paths = [f"/sapmnt/{sid}/profile/{sid}_D00_vhibr{sid_lower}ci",f"/sapmnt/{sid}/profile/{sid}_D00_vhibr{sid_lower}ai01",f"/sapmnt/{sid}/profile/DEFAULT.PFL"]
        patterns_to_delete = ["^[0-9]","^[a-zA-Z].*=$","^[a-zA-Z][^=]*$","^[^a-zA-Z0-9#_].*"]

        for each_file in file_paths:
            if os.path.exists(each_file):
                backup_file(each_file)

                delete_lines_with_specific_patterns(each_file, patterns_to_delete)
            else:
                print(f"File '{each_file}' does not exist. No actions performed.")
