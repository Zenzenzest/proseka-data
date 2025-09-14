import json

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

