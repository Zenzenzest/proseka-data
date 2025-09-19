import json
import os
from transformers.event_transformer import fetch_json_from_url, transform_jp_events, create_en_event_from_jp, update_en_events_from_en_source

def main():

    jp_events_url = "https://sekai-world.github.io/sekai-master-db-diff/events.json"
    en_events_url = "https://sekai-world.github.io/sekai-master-db-en-diff/events.json"
    event_cards_url = "https://sekai-world.github.io/sekai-master-db-diff/eventCards.json"
    
 
    jp_events_data = fetch_json_from_url(jp_events_url)
    en_events_data = fetch_json_from_url(en_events_url)
    event_cards_data = fetch_json_from_url(event_cards_url)
    
 
    existing_jp_events = []
    if os.path.exists('jp_events.json'):
        with open('jp_events.json', 'r', encoding='utf-8') as f:
            existing_jp_events = json.load(f)
    
    # Transform
    new_jp_events = transform_jp_events(jp_events_data, existing_jp_events, event_cards_data)
    
    # Merge 
    all_jp_events = existing_jp_events + new_jp_events
    with open('jp_events.json', 'w', encoding='utf-8') as f:
        json.dump(all_jp_events, f, ensure_ascii=False, indent=2)
    

    existing_en_events = []
    if os.path.exists('en_events.json'):
        with open('en_events.json', 'r', encoding='utf-8') as f:
            existing_en_events = json.load(f)
    
    # create EN events for new JP events
    new_en_events = []
    for jp_event in new_jp_events:
        en_event = create_en_event_from_jp(jp_event, event_cards_data)
        new_en_events.append(en_event)
    
    # Merge new EN events
    all_en_events = existing_en_events + new_en_events
    
    # Update EN events from EN source
    updated_en_events = update_en_events_from_en_source(en_events_data, all_en_events)
    

    with open('en_events.json', 'w', encoding='utf-8') as f:
        json.dump(updated_en_events, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(new_jp_events)} new JP events")
    print(f"Processed {len(new_en_events)} new EN events")

if __name__ == "__main__":
    main()