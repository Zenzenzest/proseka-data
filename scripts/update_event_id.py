import json
import os
import tempfile
import shutil
from typing import Dict, List

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

def add_event_ids_to_banners(jp_banners: List[Dict], en_banners: List[Dict], jp_events: List[Dict]) -> tuple:

    # Get all existing event_ids from both banner files
    existing_event_ids = set()
    for banner in jp_banners + en_banners:
        event_id = banner.get("event_id")
        if event_id:
            existing_event_ids.add(event_id)
    
    new_events = []
    for event in jp_events:
        event_id = event.get("id")
        if event_id and event_id not in existing_event_ids:
            new_events.append(event)
    print(f"Found {len(new_events)} new events to process")
    
    # Create lookup for events by ID
    event_lookup = {event.get("id"): event for event in new_events}
    
    # Add event_id to banners
    def process_banners(banners: List[Dict], banner_type: str) -> List[Dict]:
        updated_count = 0
        processed_banners = []
        
        for banner in banners:
            processed_banner = banner.copy()
            
            # Check if banner needs event_id (event-type banner without event_id)
            if (processed_banner.get("banner_type") in ["Limited Event", "Event", "Unit Limited Event"] 
                and "event_id" not in processed_banner):
                
                banner_cards = set(processed_banner.get("cards", []))

                for event_id, event in event_lookup.items():
                    event_cards = set(event.get("cards", []))
                    
                    # Check if at least 3 cards match
                    if len(banner_cards.intersection(event_cards)) >= 3:
                        processed_banner["event_id"] = event_id
                        updated_count += 1
                        print(f"Added event_id {event_id} to {banner_type} banner {processed_banner.get('id')}")
                        break
            
            processed_banners.append(processed_banner)
        
        if updated_count > 0:
            print(f"Updated {updated_count} {banner_type} banners with event_id")
        
        return processed_banners
    
    # Process both JP and EN banners
    updated_jp_banners = process_banners(jp_banners, "JP")
    updated_en_banners = process_banners(en_banners, "EN")
    
    return updated_jp_banners, updated_en_banners

def update_banners_with_event_ids():

    try:
        # Load all JSON files
        jp_banners = []
        en_banners = []
        jp_events = []
        
        if os.path.exists('jp_banners.json'):
            with open('jp_banners.json', 'r', encoding='utf-8') as f:
                jp_banners = json.load(f)
        
        if os.path.exists('en_banners.json'):
            with open('en_banners.json', 'r', encoding='utf-8') as f:
                en_banners = json.load(f)
        
        if os.path.exists('jp_events.json'):
            with open('jp_events.json', 'r', encoding='utf-8') as f:
                jp_events = json.load(f)
        
        # Add event_ids 
        updated_jp_banners, updated_en_banners = add_event_ids_to_banners(jp_banners, en_banners, jp_events)
        
        # Use temporary files to avoid unnecessary writes
        files_updated = False
        
        # Handle JP banners
        if updated_jp_banners != jp_banners:
            # Create temporary file for JP banners
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as tmp_jp:
                json.dump(updated_jp_banners, tmp_jp, ensure_ascii=False, indent=2)
                tmp_jp_path = tmp_jp.name
            
            # Compare and update if different
            if files_are_different('jp_banners.json', tmp_jp_path):
                shutil.move(tmp_jp_path, 'jp_banners.json')
                print("Updated jp_banners.json with event_id")
                files_updated = True
            else:
                os.unlink(tmp_jp_path)  
                print("No changes to jp_banners.json")
        else:
            print("No JP banners need event_id updates")
        
        # Handle EN banners
        if updated_en_banners != en_banners:
            # Create temporary file for EN banners
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as tmp_en:
                json.dump(updated_en_banners, tmp_en, ensure_ascii=False, indent=2)
                tmp_en_path = tmp_en.name
            
            # Compare and update if different
            if files_are_different('en_banners.json', tmp_en_path):
                shutil.move(tmp_en_path, 'en_banners.json')
                print("Updated en_banners.json with event_id")
                files_updated = True
            else:
                os.unlink(tmp_en_path) 
                print("No changes to en_banners.json")
        else:
            print("No EN banners need event_id updates")
            
        if not files_updated:
            print("No banner files were modified")
            
    except Exception as e:
        print(f"Error updating banners with event_id: {e}")