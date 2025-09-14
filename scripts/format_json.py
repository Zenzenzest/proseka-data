import json
import os
import glob

def format_json_with_compact_arrays(data, indent=1):

    def format_value(value, level=0):
        indent_str = " " * (indent * level)
        
        if isinstance(value, dict):
            if not value:
                return "{}"
            items = []
            for k, v in value.items():
                key_str = json.dumps(k, ensure_ascii=False)
                val_str = format_value(v, level + 1)
                items.append(f'{indent_str}{key_str}: {val_str}')
            return "{\n" + ",\n".join(items) + "\n" + " " * (indent * (level - 1)) + "}"
        
        elif isinstance(value, list):
            if not value:
                return "[]"
            # Format array elements on a single line
            elements = []
            for item in value:
                if isinstance(item, (dict, list)):
                    elements.append(json.dumps(item, separators=(',', ':'), ensure_ascii=False))
                else:
                    elements.append(json.dumps(item, ensure_ascii=False))
            return "[" + ", ".join(elements) + "]"
        
        else:
            return json.dumps(value, ensure_ascii=False)
    
    if isinstance(data, list):
        items = []
        for item in data:
            items.append(format_value(item, 1))
        return "[\n" + ",\n".join(items) + "\n]"
    else:
        return format_value(data)

def format_json_file(file_path):

    try:
        print(f"Checking {file_path}...")
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Parse the JSON data
        data = json.loads(original_content)
        
        # Format the content
        formatted_content = format_json_with_compact_arrays(data)
        
        # Only write if content actually changed
        if formatted_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            print(f"✓ Formatted {file_path}")
            return True
        else:
            print(f"- No changes needed for {file_path}")
            return False
        
    except Exception as e:
        print(f"✗ Error formatting {file_path}: {e}")
        return False

def format_all_json_files(directory=".", pattern="**/*.json"):
  

    json_files = glob.glob(os.path.join(directory, pattern), recursive=True)
    
    if not json_files:
        print("No JSON files found.")
        return
    
    print(f"Found {len(json_files)} JSON files to check:")
    
    success_count = 0
    for file_path in json_files:
        if format_json_file(file_path):
            success_count += 1
    
    if success_count > 0:
        print(f"\n✓ Formatted {success_count}/{len(json_files)} files")
    else:
        print(f"\n✓ All {len(json_files)} files are already properly formatted")

def format_specific_files(file_paths):
 
    success_count = 0
    for file_path in file_paths:
        if format_json_file(file_path):
            success_count += 1
    
    print(f"\n✓ Formatted {success_count}/{len(file_paths)} files")

if __name__ == "__main__":
    format_all_json_files()