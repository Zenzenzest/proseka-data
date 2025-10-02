import json
import os
from .transformers.banner_transformer import transform_diff, update_en_banners
from .common_update import load_json


def update_banners():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "data")
    diff_dir = os.path.join(data_dir, "diff")

    jp_diff_file = os.path.join(diff_dir, "jp_banners_diff.json")
    en_diff_file = os.path.join(diff_dir, "en_banners_diff.json")

    if not os.path.exists(jp_diff_file) and not os.path.exists(en_diff_file):
        print("No banner diff files found, stopping execution")
        return

    def load_json_with_check(path):
        if not os.path.exists(path):
            print(f"Banner diff file not found: {path}, using empty array")
            return []
        return load_json(path)

    jp_diff = load_json_with_check(jp_diff_file)
    en_diff = load_json_with_check(en_diff_file)

    if len(jp_diff) == 0 and len(en_diff) == 0:
        print("No differences found in banner diff files, stopping execution")
        return

    en_banners = load_json("en_banners.json")
    jp_banners = load_json("jp_banners.json")

    jp_cards = load_json("cards.json")

    jp_final = jp_banners.copy()  # Start with originals
    en_final = en_banners.copy()  # Start with originals

    if len(jp_diff) >= 1:
        print(f"Processing {len(jp_diff)} JP diff items")
        print(f"Original JP banners count: {len(jp_banners)}")
        print(f"Original EN banners count: {len(en_banners)}")
        
        # Show what sekai_ids exist in originals
        original_jp_sekai_ids = {banner['sekai_id'] for banner in jp_banners if 'sekai_id' in banner}
        original_en_sekai_ids = {banner['sekai_id'] for banner in en_banners if 'sekai_id' in banner}
        print(f"Original JP sekai_ids: {sorted(original_jp_sekai_ids)}")
        print(f"Original EN sekai_ids: {sorted(original_en_sekai_ids)}")
        
        # Show what's in diff
        diff_sekai_ids = {banner['id'] for banner in jp_diff}
        print(f"Diff sekai_ids: {sorted(diff_sekai_ids)}")

        transformed_jp_banners = transform_diff(
            jp_diff, "jp", jp_banners, jp_cards, en_banners)
        transformed_en_banners = transform_diff(
            jp_diff, "en", jp_banners, jp_cards, en_banners)

        print(f"Transformed JP banners count: {len(transformed_jp_banners)}")
        print(f"Transformed EN banners count: {len(transformed_en_banners)}")
        
        # Show transformed banner sekai_ids
        transformed_jp_sekai_ids = {banner['sekai_id'] for banner in transformed_jp_banners if 'sekai_id' in banner}
        transformed_en_sekai_ids = {banner['sekai_id'] for banner in transformed_en_banners if 'sekai_id' in banner}
        print(f"Transformed JP sekai_ids: {sorted(transformed_jp_sekai_ids)}")
        print(f"Transformed EN sekai_ids: {sorted(transformed_en_sekai_ids)}")

        # Create lookup sets for existing sekai_ids in the ORIGINAL arrays
        existing_jp_sekai_ids = {banner['sekai_id'] for banner in jp_banners if 'sekai_id' in banner}
        existing_en_sekai_ids = {banner['sekai_id'] for banner in en_banners if 'sekai_id' in banner}

        # Add only new JP banners (not already present in ORIGINAL)
        added_jp_count = 0
        for new_banner in transformed_jp_banners:
            sekai_id = new_banner.get('sekai_id')
            if sekai_id not in existing_jp_sekai_ids:
                jp_final.append(new_banner)
                added_jp_count += 1
                print(f"Added JP banner with sekai_id {sekai_id}")
            else:
                print(f"Skipped JP banner with sekai_id {sekai_id} - already exists")

        # Add only new EN banners (not already present in ORIGINAL)  
        added_en_count = 0
        for new_banner in transformed_en_banners:
            sekai_id = new_banner.get('sekai_id')
            if sekai_id not in existing_en_sekai_ids:
                en_final.append(new_banner)
                added_en_count += 1
                print(f"Added EN banner with sekai_id {sekai_id}")
            else:
                print(f"Skipped EN banner with sekai_id {sekai_id} - already exists")

        print(f"Added {added_jp_count} JP banners, {added_en_count} EN banners")
        print(f"Final JP count: {len(jp_final)}")
        print(f"Final EN count: {len(en_final)}")

    if len(en_diff) >= 1:
        print(f"Processing {len(en_diff)} EN diff items")
        # Update en_banners using en source
        en_final = update_en_banners(en_diff, en_final, jp_cards)
        print(f"EN final count after EN diff: {len(en_final)}")

    try:
        with open("jp_banners.json", 'w', encoding='utf-8') as f:
            json.dump(jp_final, f, indent=2, ensure_ascii=False)
        print(f"JP banners saved successfully. Count: {len(jp_final)}")
    except Exception as e:
        print(f"Error saving JP banners: {e}")

    try:
        with open("en_banners.json", 'w', encoding='utf-8') as g:
            json.dump(en_final, g, indent=2, ensure_ascii=False)
        print(f"EN banners saved successfully. Count: {len(en_final)}")
    except Exception as e:
        print(f"Error saving EN banners: {e}")