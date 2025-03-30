import json

def anonymize_speaker_data(filepath):
    """
    Reads a JSON file containing speaker data, removes address, phone, and email information,
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

    for speaker_id, speaker_info in data.items():
        speaker_info['address'] = 'N/A'
        speaker_info['phone'] = 'N/A'
        speaker_info['eMail'] = 'N/A'
        speaker_info['zipCode'] = 'N/A'
        speaker_info['city'] = 'N/A'
        speaker_info['country'] = 'N/A'

    return json.dumps(data, indent=4, ensure_ascii=False)


# Example usage (replace with your actual filepath):
filepath = '../data/speakers.json'  # Replace with your file path
modified_json = anonymize_speaker_data(filepath)

if modified_json:
    print(modified_json)
