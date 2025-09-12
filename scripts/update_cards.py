import json
import os
from transformers.cards_transformer import fetch_json_from_url, update_existing_cards, merge_card_data

def main():
    # URLs for the source JSON files (UPDATE THESE WITH YOUR ACTUAL URLs)
    jp_cards_url = "https://sekai-world.github.io/sekai-master-db-diff/cards.json"
    en_cards_url = "https://sekai-world.github.io/sekai-master-db-en-diff/cards.json"
    
    # Fetch data from both sources
    jp_cards = fetch_json_from_url(jp_cards_url)
    en_cards = fetch_json_from_url(en_cards_url)
    
    # Check if cards.json already exists
    if os.path.exists('cards.json'):
        with open('cards.json', 'r', encoding='utf-8') as f:
            existing_cards = json.load(f)
        
        # Update existing cards with new data
        processed_cards = update_existing_cards(existing_cards, jp_cards, en_cards)
    else:
        # Create new cards.json (first run)
        processed_cards = merge_card_data(jp_cards, en_cards)
    
    # Save to your cards.json
    with open('cards.json', 'w', encoding='utf-8') as f:
        json.dump(processed_cards, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(processed_cards)} cards")

if __name__ == "__main__":
    main()