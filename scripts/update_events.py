import os
import json
from .transformers.event_transformer import transform_events, update_en_events, update_event_ids
from .common_update import load_json


def update_events():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "data")
    diff_dir = os.path.join(data_dir, "diff")

    jp_diff_file = os.path.join(diff_dir, "jp_events_diff.json")
    en_diff_file = os.path.join(diff_dir, 'en_events_diff.json')

    # Check if diff files exist
    if not os.path.exists(jp_diff_file) and not os.path.exists(en_diff_file):
        print("No event diff files found, stopping execution")
        return

    # Load diff files with error handling
    def load_json_with_check(path):
        if not os.path.exists(path):
            print(f"Event diff file not found: {path}, using empty array")
            return []
        return load_json(path)

    jp_diff = load_json_with_check(jp_diff_file)
    en_diff = load_json_with_check(en_diff_file)

    # Check if both diffs are empty
    if len(jp_diff) == 0 and len(en_diff) == 0:
        print("No differences found in event diff files, stopping execution")
        return

    en_banners = load_json("en_banners.json")
    jp_banners = load_json("jp_banners.json")
    en_events = load_json("en_events.json")
    jp_events = load_json("jp_events.json")
    jp_cards = load_json("cards.json")

    jp_final = jp_events
    en_final = en_events

    transformed_jp_banners = jp_banners 
    transformed_en_banners = en_banners 

    if len(jp_diff) >= 1:
        transformed_jp_diff = transform_events(
            jp_diff, jp_events, jp_cards, "jp")
        transformed_en_diff = transform_events(
            jp_diff, jp_events, jp_cards, "en")

        transformed_jp_banners = update_event_ids(
            transformed_jp_diff, jp_banners)
        transformed_en_banners = update_event_ids(
            transformed_jp_diff, en_banners)

        jp_final = jp_events + transformed_jp_diff
        en_final = en_events + transformed_en_diff

    if len(en_diff) >= 1:
        en_final = update_en_events(en_diff, en_events)
        print("Updated EN Events from EN Diff")

    # Only save JP events if  JP diff
    if len(jp_diff) >= 1:
        try:
            with open("jp_events.json", 'w', encoding='utf-8') as f:
                json.dump(jp_final, f, indent=2, ensure_ascii=False)
            print("JP Events saved successfully")
            
            with open("jp_banners.json", 'w', encoding='utf-8') as f:
                json.dump(transformed_jp_banners, f, indent=2, ensure_ascii=False)
            print("JP Banners updated successfully")
        except Exception as e:
            print(f"Error saving JP files: {e}")

    # Only save EN events if either JP or EN diff
    if len(jp_diff) >= 1 or len(en_diff) >= 1:
        try:
            with open("en_events.json", 'w', encoding='utf-8') as g:
                json.dump(en_final, g, indent=2, ensure_ascii=False)
            print("EN Events saved successfully")
            
            # Only save EN banners if JP diff
            if len(jp_diff) >= 1:
                with open("en_banners.json", 'w', encoding='utf-8') as f:
                    json.dump(transformed_en_banners, f, indent=2, ensure_ascii=False)
                print("EN Banners updated successfully")
            else:
                print("No JP event diff, EN banners unchanged")
        except Exception as e:
            print(f"Error saving EN files: {e}")