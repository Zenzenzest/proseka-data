import os
from .common import get_json_differences, fetch_json_from_url, extract_keys_by_mode
from .common_update import  load_json, save_json


def extract_and_diff(mode):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir,"data")
    extracted_dir = os.path.join(data_dir,"extracted")
    diff_dir = os.path.join(data_dir,"diff")
    jp_cards_url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/cards.json"
    en_cards_url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/refs/heads/main/cards.json"
    jp_banners_url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/gachas.json"
    en_banners_url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/refs/heads/main/gachas.json"
    jp_events_url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/events.json"
    en_events_url = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/refs/heads/main/events.json"

    jp_cards_master = os.path.join(data_dir,"master","jp_cards_orig.json")
    en_cards_master = os.path.join(data_dir,"master", "en_cards_orig.json")
    jp_banners_master = os.path.join(data_dir,"master","jp_banners_orig.json")
    en_banners_master= os.path.join(data_dir, "master","en_banners_orig.json")
    jp_events_master = os.path.join(data_dir,"master","jp_events_orig.json")
    en_events_master = os.path.join(data_dir,"master","en_events_orig.json")
    
    jp_cards_extracted = os.path.join(extracted_dir, "jp_cards_extracted.json")
    en_cards_extracted = os.path.join(extracted_dir, "en_cards_extracted.json")
    jp_banners_extracted = os.path.join(extracted_dir, "jp_banners_extracted.json")
    en_banners_extracted = os.path.join(extracted_dir, "en_banners_extracted.json")
    jp_events_extracted = os.path.join(extracted_dir, "jp_events_extracted.json")
    en_events_extracted = os.path.join(extracted_dir, "en_events_extracted.json")

    if mode=="sekai":
        jp_cards_sekai = fetch_json_from_url(jp_cards_url)
        en_cards_sekai = fetch_json_from_url(en_cards_url)
        jp_banners_sekai = fetch_json_from_url(jp_banners_url)
        en_banners_sekai = fetch_json_from_url(en_banners_url)
        jp_events_sekai = fetch_json_from_url(jp_events_url)
        en_events_sekai = fetch_json_from_url(en_events_url)

        jp_cards_extracted_sekai = extract_keys_by_mode(jp_cards_sekai, "cards")
        en_cards_extracted_sekai = extract_keys_by_mode(en_cards_sekai,"cards")
        jp_banners_extracted_sekai = extract_keys_by_mode(jp_banners_sekai,"banner")
        en_banners_extracted_sekai = extract_keys_by_mode(en_banners_sekai,"banner")
        jp_events_extracted_sekai = extract_keys_by_mode(jp_events_sekai,"event")
        en_events_extracted_sekai = extract_keys_by_mode(en_events_sekai,"event")
        
        jp_cards_diff = get_json_differences(load_json(jp_cards_extracted), jp_cards_extracted_sekai, "cards")
        en_cards_diff = get_json_differences(load_json(en_cards_extracted),en_cards_extracted_sekai, "cards")
        jp_banners_diff = get_json_differences(load_json(jp_banners_extracted),jp_banners_extracted_sekai)
        en_banners_diff = get_json_differences(load_json(en_banners_extracted),en_banners_extracted_sekai)
        jp_events_diff = get_json_differences(load_json(jp_events_extracted),jp_events_extracted_sekai)
        en_events_diff = get_json_differences(load_json(en_events_extracted),en_events_extracted_sekai)

        diffs = [
            (jp_cards_diff, "jp_cards_diff.json", jp_cards_extracted_sekai, jp_cards_extracted, "jp_cards"),
            (en_cards_diff, "en_cards_diff.json", en_cards_extracted_sekai, en_cards_extracted, "en_cards"),
            (jp_banners_diff, "jp_banners_diff.json", jp_banners_extracted_sekai, jp_banners_extracted, "jp_banners"),
            (en_banners_diff, "en_banners_diff.json", en_banners_extracted_sekai, en_banners_extracted, "en_banners"),
            (jp_events_diff, "jp_events_diff.json", jp_events_extracted_sekai, jp_events_extracted, "jp_events"),
            (en_events_diff, "en_events_diff.json", en_events_extracted_sekai, en_events_extracted, "en_events")
        ]

        os.makedirs(diff_dir, exist_ok=True)

        files_with_diffs = []

        for diff, filename, extracted_new, extracted_path, file_type in diffs:
            if len(diff) > 0:
                save_json(os.path.join(diff_dir, filename), diff)
                save_json(extracted_path, extracted_new)
                files_with_diffs.append(file_type)

        if files_with_diffs:
            print(f"Files with differences: {', '.join(files_with_diffs)}")
        else:
            print("All files have 0 differences")


    elif mode=="local":
        jp_cards_extracted_master = extract_keys_by_mode(load_json(jp_cards_master), "cards")
        en_cards_extracted_master = extract_keys_by_mode(load_json(en_cards_master),"cards")
        jp_banners_extracted_master = extract_keys_by_mode(load_json(jp_banners_master),"banner")
        en_banners_extracted_master = extract_keys_by_mode(load_json(en_banners_master),"banner")
        jp_events_extracted_master = extract_keys_by_mode(load_json(jp_events_master),"event")
        en_events_extracted_master = extract_keys_by_mode(load_json(en_events_master),"event")

        jp_cards_diff = get_json_differences(load_json(jp_cards_extracted), jp_cards_extracted_master, "cards")
        en_cards_diff = get_json_differences(load_json(en_cards_extracted),en_cards_extracted_master, "cards")
        jp_banners_diff = get_json_differences(load_json(jp_banners_extracted),jp_banners_extracted_master)
        en_banners_diff = get_json_differences(load_json(en_banners_extracted),en_banners_extracted_master)
        jp_events_diff = get_json_differences(load_json(jp_events_extracted),jp_events_extracted_master)
        en_events_diff = get_json_differences(load_json(en_events_extracted),en_events_extracted_master)

        diffs = [
            (jp_cards_diff, "jp_cards_diff.json", jp_cards_extracted_master, jp_cards_extracted, "jp_cards"),
            (en_cards_diff, "en_cards_diff.json", en_cards_extracted_master, en_cards_extracted, "en_cards"),
            (jp_banners_diff, "jp_banners_diff.json", jp_banners_extracted_master, jp_banners_extracted, "jp_banners"),
            (en_banners_diff, "en_banners_diff.json", en_banners_extracted_master, en_banners_extracted, "en_banners"),
            (jp_events_diff, "jp_events_diff.json", jp_events_extracted_master, jp_events_extracted, "jp_events"),
            (en_events_diff, "en_events_diff.json", en_events_extracted_master, en_events_extracted, "en_events")
        ]

        os.makedirs(diff_dir, exist_ok=True)

        files_with_diffs = []

        for diff, filename, extracted_new, extracted_path, file_type in diffs:
            if len(diff) > 0:
                save_json(os.path.join(diff_dir, filename), diff)
                save_json(extracted_path, extracted_new)
                files_with_diffs.append(file_type)

        if files_with_diffs:
            print(f"Files with differences: {', '.join(files_with_diffs)}")
        else:
            print("All files have 0 differences")
 