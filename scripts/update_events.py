import json
import os
import tempfile
import shutil
from transformers.cards_transformer import fetch_json_from_url, update_existing_cards, merge_card_data
from common_update import files_are_different


def main():
    # sources
    jp_cards_url = "https://sekai-world.github.io/sekai-master-db-diff/cards.json"
    en_cards_url = "https://sekai-world.github.io/sekai-master-db-en-diff/cards.json"
    
  
    jp_cards = fetch_json_from_url(jp_cards_url)
    en_cards = fetch_json_from_url(en_cards_url)
    

    if os.path.exists('cards.json'):
        with open('cards.json', 'r', encoding='utf-8') as f:
            existing_cards = json.load(f)
        
        # Update existing cards with new data
        processed_cards = update_existing_cards(existing_cards, jp_cards, en_cards)
    else:
        # Create new cards.json (first run)
        processed_cards = merge_card_data(jp_cards, en_cards)
    

    if not os.path.exists('cards.json'):
      
        with open('cards.json', 'w', encoding='utf-8') as f:
            json.dump(processed_cards, f, ensure_ascii=False, indent=2)
        print(f"Created cards.json with {len(processed_cards)} cards")
    else:

 
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as tmp_cards:
            json.dump(processed_cards, tmp_cards, ensure_ascii=False, indent=2)
            tmp_cards_path = tmp_cards.name
        
        # Compare and update if different
        if files_are_different('cards.json', tmp_cards_path):
            shutil.move(tmp_cards_path, 'cards.json')
            print(f"Updated cards.json with {len(processed_cards)} cards")
        else:
            os.unlink(tmp_cards_path) 
            print("No changes to cards.json")

if __name__ == "__main__":
    main()