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

    jp_final = jp_banners
    en_final = en_banners

    if len(jp_diff) >= 1:
        transformed_jp_banners = transform_diff(
            jp_diff, "jp", jp_banners, jp_cards, en_banners)
        transformed_en_banners = transform_diff(
            jp_diff, "en", jp_banners, jp_cards, en_banners)

        jp_final = jp_banners + transformed_jp_banners
        en_final = en_banners + transformed_en_banners

        print(f"JP final count after JP diff: {len(jp_final)}")
        print(f"EN final count after JP diff: {len(en_final)}")

    if len(en_diff) >= 1:
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