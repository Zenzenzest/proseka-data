import subprocess
import sys
import os
import json
import hashlib
from scripts.format_json import format_all_json_files
from scripts.update_event_id import update_banners_with_event_ids

def get_file_hash(filename):
    """Get MD5 hash of file content"""
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_json_files_state():
    """Get the current state (hashes) of all JSON files"""
    json_files = [
        'cards.json',
        'jp_banners.json', 
        'en_banners.json',
        'jp_events.json',
        'en_events.json',
        'master/en.json', 
        'master/jp.json'
    ]
    
    file_states = {}
    for filename in json_files:
        if os.path.exists(filename):
            file_states[filename] = get_file_hash(filename)
    
    return file_states

def run_script(script_name):
    """Run a Python script and check for errors"""
    try:
        print(f"Running {script_name}...")
        result = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    # initial state of JSON files
    print("Checking initial file states...")
    initial_states = get_json_files_state()
    
    scripts = [
        'scripts/update_cards.py',
        'scripts/update_banners.py', 
        'scripts/update_events.py',
    ]
    
    success = True
    for script in scripts:
        if not run_script(script):
            success = False
    
    if success:
        #state after running scripts
        after_scripts_states = get_json_files_state()
        
        # Check if any files were modified 
        files_modified = False
        
        # Check for content changes in existing files
        for filename, initial_hash in initial_states.items():
            current_hash = after_scripts_states.get(filename)
            if current_hash != initial_hash:
                files_modified = True
                print(f"Detected changes in {filename}")
                break
        
        # Check for new files
        if not files_modified:
            for filename, current_hash in after_scripts_states.items():
                if filename not in initial_states:
                    files_modified = True
                    print(f"Detected new file: {filename}")
                    break
        

        # Add event_id to banners
        print("Adding event_id to banners...")
        update_banners_with_event_ids()
        
        # Get final state after adding event_id
        final_states = get_json_files_state()
        
        # Check if files were modified by adding event_id
        if not files_modified:
            for filename, after_hash in after_scripts_states.items():
                final_hash = final_states.get(filename)
                if final_hash != after_hash:
                    files_modified = True
                    print(f"Detected changes in {filename} (event_id update)")
                    break
        
        # Format JSON files only if files were modified
        if files_modified:
            print("Files were modified, formatting JSON files...")
            format_all_json_files()
            print("✓ All updates completed successfully!")
        else:
            print("No files were modified, skipping formatting")
            print("✓ All updates completed successfully!")
    else:
        print("Some scripts failed. Check the errors above.")

if __name__ == "__main__":
    main()