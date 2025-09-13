import subprocess
import sys
from scripts.format_json import format_all_json_files

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
 
    scripts = [
        'scripts/update_cards.py',
        'scripts/update_banners.py', 
        'scripts/update_events.py'
    ]
    
    success = True
    for script in scripts:
        if not run_script(script):
            success = False
    
    if success:

        print("Formatting JSON files...")
        format_all_json_files()
        print("All updates completed successfully!")
    else:
        print("Some scripts failed. Check the errors above.")

if __name__ == "__main__":
    main()