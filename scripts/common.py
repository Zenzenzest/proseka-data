import json
from typing import List, Dict, Any
import requests


def get_json_differences(
    old_data: List[Dict[str, Any]],
    new_data: List[Dict[str, Any]],
    mode: str = None,
    key: str = "id"
) -> List[Dict[str, Any]]:

    if mode == "cards":
        if not old_data:
            return new_data
        max_old_id = old_data[-1][key]
        return [obj for obj in new_data if obj[key] > max_old_id]
    else:
        old_keys = {obj[key] for obj in old_data}
        return [obj for obj in new_data if obj[key] not in old_keys]

def save_json_pretty_inline_arrays(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i, obj in enumerate(data):
            obj_copy = obj.copy()
            # Convert lists to inline strings
            for key, value in obj.items():
                if isinstance(value, list):
                    obj_copy[key] = json.dumps(value, ensure_ascii=False)
            # Dump the object with indent for top-level keys
            obj_str = json.dumps(obj_copy, ensure_ascii=False, indent=1)

            for key, value in obj_copy.items():
                if isinstance(obj[key], list):
                    obj_str = obj_str.replace(f'"{value}"', value)
            # Add comma if not last object
            if i < len(data) - 1:
                obj_str += ","
            f.write(obj_str + "\n")
        f.write("]\n")


def extract_keys_by_mode(json_array: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
    mode_keys = {
        "cards": ["id", "characterId", "attr", "cardRarityType", "cardSupplyId", "prefix", "releaseAt"],
        "banner": ["id", "name", "endAt", "startAt", "gachaPickups", "gachaDetails"],
        "event": ["id", "unit", "eventType", "name", "startAt", "aggregateAt", "closedAt"],
    }


    keys_to_keep = mode_keys.get(mode)
    if not keys_to_keep:
        raise ValueError(f"No keys defined for mode '{mode}'")


    return [{k: obj[k] for k in keys_to_keep if k in obj} for obj in json_array]

def extract_keys_by_mode_debug(json_array: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
    mode_keys = {
        "cards": ["id", "characterId", "attr", "cardRarityType", "cardSupplyId", "prefix", "releaseAt"],
        "banner": ["id", "name", "endAt", "startAt", "gachaPickups", "gachaDetails"],
        "event": ["id", "name", "endAt", "startAt", "gachaPickups", "gachaDetails"],
    }

    keys_to_keep = mode_keys.get(mode)
    if not keys_to_keep:
        raise ValueError(f"No keys defined for mode '{mode}'")

    print(f"Looking for keys: {keys_to_keep}")
    
    if not json_array:
        print("JSON array is empty!")
        return []
    
    print(f"First item in array: {json_array[0]}")
    print(f"Available keys in first item: {list(json_array[0].keys()) if isinstance(json_array[0], dict) else 'Not a dict'}")
    
    # Check which keys actually exist
    available_keys = set(json_array[0].keys()) if isinstance(json_array[0], dict) else set()
    missing_keys = [k for k in keys_to_keep if k not in available_keys]
    found_keys = [k for k in keys_to_keep if k in available_keys]
    
    print(f"Keys found in data: {found_keys}")
    print(f"Missing keys: {missing_keys}")
    
    # Extract keys
    result = []
    for obj in json_array:
        if isinstance(obj, dict):
            extracted_obj = {k: obj[k] for k in keys_to_keep if k in obj}
            if extracted_obj:  # Only add if we found at least one key
                result.append(extracted_obj)
    
    print(f"Extracted {len(result)} objects")
    return result
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def fetch_json_from_url(url: str) -> Dict:
    """Fetch JSON data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()