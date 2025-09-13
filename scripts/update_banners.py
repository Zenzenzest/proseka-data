import json
import os
from transformers.banner_transformer import fetch_json_from_url, transform_jp_banners,create_en_banner_from_jp, update_jp_banners_with_en_ids, update_en_banners_from_en_source

def main():
    # sources
    jp_gachas_url = "https://sekai-world.github.io/sekai-master-db-diff/gachas.json"
    en_gachas_url = "https://sekai-world.github.io/sekai-master-db-en-diff/gachas.json"
    

    jp_gachas = fetch_json_from_url(jp_gachas_url)
    en_gachas = fetch_json_from_url(en_gachas_url)
    
    # Load cards data for banner type
    cards_data = []
    if os.path.exists('cards.json'):
        with open('cards.json', 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
    
    # load  JP banners
    existing_jp_banners = []
    if os.path.exists('jp_banners.json'):
        with open('jp_banners.json', 'r', encoding='utf-8') as f:
            existing_jp_banners = json.load(f)
    

    new_jp_banners = transform_jp_banners(jp_gachas, existing_jp_banners, cards_data)
    

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
    
    updated_en_banners = update_en_banners_from_en_source(en_gachas, all_en_banners)
    
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

if __name__ == "__main__":
    main()