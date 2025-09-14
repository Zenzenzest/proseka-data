import json
import os
from transformers.banner_transformer import fetch_json_from_url, transform_jp_banners,create_en_banner_from_jp, update_jp_banners_with_en_ids, update_en_banners_from_en_source
from common_update import load_json, get_new_entries,save_json
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)


    jp_gachas_url = "https://sekai-world.github.io/sekai-master-db-diff/gachas.json"
    en_gachas_url = "https://sekai-world.github.io/sekai-master-db-en-diff/gachas.json"
    
    jp_copy = os.path.join(parent_dir, 'master', 'jp.json')
    en_copy = os.path.join(parent_dir, 'master', 'en.json')
    jp_master = fetch_json_from_url(jp_gachas_url)
    en_master = fetch_json_from_url(en_gachas_url)



    en_gc = load_json(en_copy)
    jp_gc = load_json(jp_copy)
    en_diff = get_new_entries(en_gc,en_master)
    jp_diff = get_new_entries(jp_gc, jp_master)
 
    

    #    Load cards data for banner type
    cards_data = []
    if os.path.exists('cards.json'):
        with open('cards.json', 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
    
    # load  JP banners
    existing_jp_banners = []
    if os.path.exists('jp_banners.json'):
        with open('jp_banners.json', 'r', encoding='utf-8') as f:
            existing_jp_banners = json.load(f)
    

    new_jp_banners = transform_jp_banners(jp_diff, existing_jp_banners, cards_data)
    

    all_jp_banners = existing_jp_banners + new_jp_banners
    

    existing_en_banners = []
    if os.path.exists('en_banners.json'):
        with open('en_banners.json', 'r', encoding='utf-8') as f:
            existing_en_banners = json.load(f)
    
    # Create corresponding EN banners for new JP banners
    all_en_banners_so_far = existing_en_banners.copy()
    new_en_banners = []
    
    for jp_banner in new_jp_banners:
        en_banner = create_en_banner_from_jp(jp_banner, all_en_banners_so_far, all_jp_banners)
        new_en_banners.append(en_banner)
        all_en_banners_so_far.append(en_banner)
    
    # Merge
    all_en_banners = existing_en_banners + new_en_banners
    
    updated_en_banners = update_en_banners_from_en_source(en_diff, all_en_banners)
    
    # Update JP banners with en_id from EN 
    updated_jp_banners = update_jp_banners_with_en_ids(all_jp_banners, updated_en_banners)
    
    # Save to jp_banners.json
    with open('jp_banners.json', 'w', encoding='utf-8') as f:
        json.dump(updated_jp_banners, f, ensure_ascii=False, indent=2)
    
    # Save to en_banners.json
    with open('en_banners.json', 'w', encoding='utf-8') as f:
        json.dump(updated_en_banners, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(new_jp_banners)} new JP banners")
    print(f"Processed {len(new_en_banners)} new EN banners")

    # Overwrites my en.json and jp.json if new entries
    try:
  
        if en_diff: 
            save_json(en_master, en_copy)
            print(f"Updated local EN copy: {en_copy}")
        else:
            print("No new EN entries, skipping EN update")
        
 
        if jp_diff: 
            save_json(jp_master, jp_copy)
            print(f"Updated local JP copy: {jp_copy}")
        else:
            print("No new JP entries, skipping JP update")
    
    except Exception as e:
        print(f"Warning: Could not update local copies - {e}")

if __name__ == "__main__":
    main()