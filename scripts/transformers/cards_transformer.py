import pytz
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import deepl
import os
from .common_transform import get_pst_pdt_status

load_dotenv()

def get_api_keys():
    """Get API keys from environment variables"""
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    deepl_api_key = os.getenv('DEEPL_API_KEY')
    return deepseek_api_key, deepl_api_key

from .mappings import (
    CHARACTERS, RARITY_MAPPINGS, CARD_SUPPLY_MAPPINGS, CARD_UNIT_MAPPINGS, SUB_UNIT_MAPPINGS
)
import re
from datetime import datetime, timedelta


EVENT_CARDS_URL = "https://sekai-world.github.io/sekai-master-db-diff/eventCards.json"
EVENT_DECK_BONUSES_URL = "https://sekai-world.github.io/sekai-master-db-diff/eventDeckBonuses.json"


def fetch_json_from_url(url: str) -> Dict:
    """Fetch JSON data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()




# TRANSLATOR
def get_deepl_api_key():
    """Get DeepL API key from environment variables"""
    return os.getenv('DEEPL_API_KEY')

def translate_jp_to_en(jp_text: str) -> str:
    """Translate JP text to English using DeepL API"""
    deepl_api_key = get_deepl_api_key()
    
    if not deepl_api_key:
        print("DeepL API key not found")
        return ""
    
    try:
        deepl_client = deepl.Translator(deepl_api_key)
        result = deepl_client.translate_text(jp_text, target_lang="EN-US")
        return result.text
    except Exception as e:
        print(f"DeepL translation failed: {e}")
        return ""


# BIRTHDAY CARD NAME
def get_birthday_card_name(jp_prefix: str) -> str:
    """Get English name for birthday cards by adding 1 year to the date in JP prefix"""
    if not jp_prefix:
        return ""
    

    year_pattern = r'(\d{4})'
    match = re.search(year_pattern, jp_prefix)
    
    if match:
        current_year = int(match.group(1))
        next_year = current_year + 1
        # Replace the year in the JP prefix
        return re.sub(year_pattern, str(next_year), jp_prefix)
    
    return jp_prefix 







def calculate_en_release_time(jp_release_time_ms: int) -> int:
    """Calculate EN release time based on JP release time and current timezone"""
    if jp_release_time_ms == 0:
        return 0
    

    jp_release_dt = datetime.fromtimestamp(jp_release_time_ms / 1000, tz=pytz.UTC)
    
 
    en_release_dt = jp_release_dt.replace(year=jp_release_dt.year + 1)
    

    timezone = get_pst_pdt_status()
    if timezone == "PDT":
        # add 16 hours for PDT
        en_release_dt = en_release_dt + timedelta(hours=16)
    else:
        # add 17 hours for PST
        en_release_dt = en_release_dt + timedelta(hours=17)
    
    # Convert back to milliseconds
    return int(en_release_dt.timestamp() * 1000)





def get_character_name(character_id: int) -> str:
    """Convert character ID to character name"""
    try:
        # characterId is 1-indexed, CHARACTERS is 0-indexed
        return CHARACTERS[character_id - 1]
    except IndexError:
        return ""

def get_unit_name(character_name: str) -> str:
    """Get unit name based on character name"""
    for unit, characters in CARD_UNIT_MAPPINGS.items():
        if character_name in characters:
            return unit
    return ""

def capitalize_attr(attr: str) -> str:
    """Convert attribute to capitalized format"""
    return attr.capitalize()

def convert_rarity(card_rarity_type: str) -> int:
    """Convert card rarity type to number"""
    return RARITY_MAPPINGS.get(card_rarity_type, 1)

def convert_card_type(card_supply_id: int) -> str:
    """Convert card supply ID to card type"""
    return CARD_SUPPLY_MAPPINGS.get(card_supply_id, "permanent")


def get_sub_unit(card_id: int) -> Optional[str]:
    """Get sub_unit for Virtual Singer cards using event data"""
    try:
        event_cards = fetch_json_from_url(EVENT_CARDS_URL)
        events = fetch_json_from_url("https://sekai-world.github.io/sekai-master-db-diff/events.json")
        
        # Step 1: Find matching event card by cardId
        matching_event_card = None
        for event_card in event_cards:
            if event_card.get("cardId") == card_id:
                matching_event_card = event_card
                break
        
        if not matching_event_card:
            return None
            
        # Step 2: Get eventId from the matching event card
        event_id = matching_event_card.get("eventId")
        if not event_id:
            return None
            
        # Step 3: Find matching event by eventId
        matching_event = None
        for event in events:
            if event.get("id") == event_id:
                matching_event = event
                break
        
        if not matching_event:
            return None
            
        # Step 4: Get unit from event and map it
        event_unit = matching_event.get("unit")
        return SUB_UNIT_MAPPINGS.get(event_unit)
    
    except Exception:
        # If fails, return None
        return None



def get_virtual_singer_char_id(card_id: int) -> Optional[int]:
    """Get character ID for Virtual Singer cards using event data"""
    try:
        # Fetch the required JSON files
        event_cards = fetch_json_from_url(EVENT_CARDS_URL)
        event_deck_bonuses = fetch_json_from_url(EVENT_DECK_BONUSES_URL)
        
        # Step 1: Find matching event card by cardId
        matching_event_card = None
        for event_card in event_cards:
            if event_card.get("cardId") == card_id:
                matching_event_card = event_card
                break
        
        if not matching_event_card:
            return None
            
        # Step 2: Get eventId from the matching event card
        event_id = matching_event_card.get("eventId")
        if not event_id:
            return None
            
        # Step 3: Find first 5 matching event deck bonuses by eventId
        matching_bonuses = []
        for bonus in event_deck_bonuses:
            if bonus.get("eventId") == event_id:
                matching_bonuses.append(bonus)
                if len(matching_bonuses) == 5:
                    break
        
        # Step 4: Find the one with gameCharacterUnitId > 20
        for bonus in matching_bonuses:
            game_char_unit_id = bonus.get("gameCharacterUnitId", 0)
            if game_char_unit_id > 20:
                return game_char_unit_id
                
        return None
    except Exception:
        # If  fails, fall back to normal mapping
        return None



def get_character_id(character_name: str, unit: str, card_id: int) -> int:
    """Get character ID based on character name and unit"""
    # complex lookup first for VS
    if unit == "Virtual Singers":
        virtual_char_id = get_virtual_singer_char_id(card_id)
        if virtual_char_id:
            return virtual_char_id
    

    # fall back to normal mapping for non-VS or if lookup failed
    try:
   
        return CHARACTERS.index(character_name) + 1
    except ValueError:
        return 0 


# MERGE
def merge_card_data(jp_cards: List[Dict], en_cards: List[Dict]) -> List[Dict]:

    # lookup dictionaries
    en_cards_dict = {card['id']: card for card in en_cards}
    jp_cards_dict = {card['id']: card for card in jp_cards}
    
    result = []
    processed_ids = set()
    

    for card_id in jp_cards_dict.keys():
        jp_card = jp_cards_dict[card_id]
        en_card = en_cards_dict.get(card_id)
        
        if en_card:
            processed_card = {
                "id": card_id,
                "name": en_card.get("prefix", ""),
                "jp_name": jp_card.get("prefix", ""),
                "attribute": capitalize_attr(jp_card.get("attr", "")),
                "rarity": convert_rarity(jp_card.get("cardRarityType", "rarity_1")),
                "card_type": convert_card_type(jp_card.get("cardSupplyId", 1)),
                "jp_released": jp_card.get("releaseAt", 0),
                "en_released": en_card.get("releaseAt", 0),
                "character": "",
                "unit": "",
                "charId": jp_card.get("characterId", 0)
            }
            result.append(processed_card)
            processed_ids.add(card_id)
    

    #  JP-only cards (not yet released in EN)
    for card_id in jp_cards_dict.keys():
        if card_id not in processed_ids:
            jp_card = jp_cards_dict[card_id]
            processed_card = {
                "id": card_id,
                "name": "", 
                "jp_name": jp_card.get("prefix", ""),
                "attribute": capitalize_attr(jp_card.get("attr", "")),
                "rarity": convert_rarity(jp_card.get("cardRarityType", "rarity_1")),
                "card_type": convert_card_type(jp_card.get("cardSupplyId", 1)),
                "jp_released": jp_card.get("releaseAt", 0),
                "en_released": 0, 
                "character": "",
                "unit": "",
                "charId": jp_card.get("characterId", 0)
            }
            result.append(processed_card)
    return result






def update_existing_cards(existing_cards: List[Dict], jp_cards: List[Dict], en_cards: List[Dict]) -> List[Dict]:
    """Update existing cards.json with new EN data when available"""
    # create lookup dictionaries
    en_cards_dict = {card['id']: card for card in en_cards}
    jp_cards_dict = {card['id']: card for card in jp_cards}
    
    # Convert cards to dictionary for easier lookup
    existing_dict = {card['id']: card for card in existing_cards}
    updated_count = 0
    
    # update existing cards with new EN data only
    for card_id, existing_card in existing_dict.items():
        en_card = en_cards_dict.get(card_id)
        jp_card = jp_cards_dict.get(card_id)
        
        original_card = existing_card.copy()  # keep copy to check for changes
        

        if en_card:
    
            if existing_card.get("name") != en_card.get("prefix", ""):
                existing_card["name"] = en_card.get("prefix", "")
            if existing_card.get("en_released") != en_card.get("releaseAt", 0):
                existing_card["en_released"] = en_card.get("releaseAt", 0)
        
        # Check if my card is actually modified
        if existing_card != original_card:
            updated_count += 1
    
    # Add completely new JP cards 
    new_count = 0
    for card_id, jp_card in jp_cards_dict.items():
        if card_id not in existing_dict:
            character_id = jp_card.get("characterId", 0)
            character_name = get_character_name(character_id)
            unit = get_unit_name(character_name)
            
      
            char_id = get_character_id(character_name, unit, card_id)
            

            jp_release_time = jp_card.get("releaseAt", 0)
            
            if jp_release_time > 0:
                en_release_time = calculate_en_release_time(jp_release_time)
            else:
                en_release_time = 0
                
            # card name - special handling for different card types
            jp_prefix = jp_card.get("prefix", "")
            card_rarity = convert_rarity(jp_card.get("cardRarityType", "rarity_1"))
            
            if card_rarity == 5:  # Bday/Anniv card
                initial_name = get_birthday_card_name(jp_prefix)
            else:
                # Try to translate JP prefix to English
                translated_name = translate_jp_to_en(jp_prefix)
                initial_name = translated_name if translated_name else ""
            
            # card structure
            new_card = {
                "id": card_id,
                "name": initial_name, 
                "jp_name": jp_prefix,
                "attribute": capitalize_attr(jp_card.get("attr", "")),
                "rarity": card_rarity,
                "card_type": convert_card_type(jp_card.get("cardSupplyId", 1)),
                "jp_released": jp_release_time,
                "en_released": en_release_time,
                "charId": char_id,
                "character": character_name,
                "unit": unit
            }
            
            # sub_unit for VS
            if unit == "Virtual Singers":
                sub_unit = get_sub_unit(card_id)
                if sub_unit:
                    new_card["sub_unit"] = sub_unit
            
            existing_dict[card_id] = new_card
            new_count += 1
    
    if updated_count > 0 or new_count > 0:
        print(f"Updated {updated_count} cards, added {new_count} new cards")
    
    return list(existing_dict.values())