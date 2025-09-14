import json
import os

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_new_entries(old_arr, new_arr):
    old_set = {json.dumps(obj, sort_keys=True) for obj in old_arr}
    new_set = {json.dumps(obj, sort_keys=True) for obj in new_arr}
    diff = new_set - old_set    
    return [json.loads(obj) for obj in diff]

def files_are_different(file1_path, file2_path):
    """Compare two JSON files for content differences"""
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return True
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1:
            data1 = json.load(f1)
        with open(file2_path, 'r', encoding='utf-8') as f2:
            data2 = json.load(f2)
        return data1 != data2
    except:
        return True