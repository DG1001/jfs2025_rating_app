import json

def anonymize_user_data(filepath):
    """
    Reads a JSON file containing user data, removes email information,
    and returns the modified JSON data.

    Args:
        filepath: The path to the JSON file.

    Returns:
        A string containing the modified JSON data.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return None

    for user_id, user_info in data.items():
        # Skip anonymizing the admin user
        if user_id == 'admin':
            continue
            
        # Fully anonymize email (remove domain too)
        if 'email' in user_info:
            user_info['email'] = "anonymous@example.com"

    return json.dumps(data, indent=4, ensure_ascii=False)


# Example usage (replace with your actual filepath):
filepath = '../data/users.json'  # Replace with your file path
modified_json = anonymize_user_data(filepath)

if modified_json:
    print(modified_json)
