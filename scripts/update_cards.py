import json
import os
from .transformers.cards_transformer import transform_diff, update_en_cards
from .common_update import load_json

def update_cards():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir,"data")

    en_diff_file = os.path.join(data_dir,"diff","en_cards_diff.json")
    jp_diff_file = os.path.join(data_dir, "diff", "jp_cards_diff.json")

    if not os.path.exists(jp_diff_file) and not os.path.exists(en_diff_file):
        print("No card diff files found, stopping execution")
        return


    def load_json_with_check(path):
        if not os.path.exists(path):
            print(f"Card diff file not found: {path}, using empty array")
            return []
        return load_json(path)

    jp_diff = load_json_with_check(jp_diff_file)
    en_diff = load_json_with_check(en_diff_file)


    if len(jp_diff) == 0 and len(en_diff) == 0:
        print("No differences found in card diff files, stopping execution")
        return

    with open('cards.json', 'r', encoding='utf-8') as c:
        my_cards = json.load(c)

    my_cards_file = os.path.join(parent_dir, "cards.json")

    final_cards = my_cards

    if len(jp_diff) >= 1:
        transformed_jp_diff = transform_diff(jp_diff, mode="jp")
    
        final_cards = final_cards + transformed_jp_diff  
        
        with open(jp_diff_file, 'w', encoding='utf-8') as f:
            json.dump(transformed_jp_diff, f, indent=2, ensure_ascii=False)

    if len(en_diff) >= 1:
        transformed_en_diff = transform_diff(en_diff, mode="en")
        final_cards = update_en_cards(final_cards, transformed_en_diff)
        print("EN cards updated")
        
        with open(en_diff_file, 'w', encoding='utf-8') as f:
            json.dump(transformed_en_diff, f, indent=2, ensure_ascii=False)

    with open(my_cards_file, 'w', encoding='utf-8') as f:
        json.dump(final_cards, f, indent=2, ensure_ascii=False)

    print(f"Final merged data saved. Total cards: {len(final_cards)}")