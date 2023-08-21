
import json
import sys


def read_json_file(filepath):
    """Reads and returns data from a JSON file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def validate_data(data):
    """Validates the structure and content of the input data."""
    if not isinstance(data, list):
        print("Error: Data should be a list of process details.")
        sys.exit(1)

    for entry in data:
        if not isinstance(entry, dict):
            print("Error: Each entry in the list should be a dictionary.")
            sys.exit(1)

        for process in entry:
            # Check 'process_name'
            if "process_name" not in entry[process]:
                print(f"Error: 'process_name' key missing in entry for process '{process}'.")
                sys.exit(1)
            if not isinstance(entry[process]["process_name"], str):
                print(f"Error: 'process_name' should be a string for process '{process}'.")
                sys.exit(1)

            # Check 'hourly_rate'
            if "hourly_rate" not in entry[process]:
                print(f"Error: 'hourly_rate' key missing in entry for process '{process}'.")
                sys.exit(1)
            if not isinstance(entry[process]["hourly_rate"], (int, float)):
                print(f"Error: 'hourly_rate' should be a number for process '{process}'.")
                sys.exit(1)

            # Check 'dynamic_value'
            if "dynamic_value" not in entry[process]:
                print(f"Error: 'dynamic_value' key missing in entry for process '{process}'.")
                sys.exit(1)
            if not isinstance(entry[process]["dynamic_value"], str):
                print(f"Error: 'dynamic_value' should be a string for process '{process}'.")
                sys.exit(1)

            # Check 'time_hrs'
            if "time_hrs" not in entry[process]:
                print(f"Error: 'time_hrs' key missing in entry for process '{process}'.")
                sys.exit(1)
            if not isinstance(entry[process]["time_hrs"], dict):
                print(f"Error: 'time_hrs' should be a dictionary for process '{process}'.")
                sys.exit(1)
            if "before" not in entry[process]["time_hrs"] or "after" not in entry[process]["time_hrs"]:
                print(f"Error: 'before' or 'after' keys missing in 'time_hrs' for process '{process}'.")
                sys.exit(1)
            if not isinstance(entry[process]["time_hrs"]["before"], (int, float)) or not isinstance(entry[process]["time_hrs"]["after"], (int, float)):
                print(f"Error: 'before' and 'after' in 'time_hrs' should be numbers for process '{process}'.")
                sys.exit(1)

    print("Data is valid!")


if __name__ == "__main__":
    # Validate the input data
    data = read_json_file('src/value/converted_test.json')
    validate_data(data)

 