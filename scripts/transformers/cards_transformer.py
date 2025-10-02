import pytz
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import deepl
import os
from .common_transform import get_pst_pdt_status
from .mappings import UPCOMING_COLLAB_TAG

from .mappings import (
    CHARACTERS, RARITY_MAPPINGS, CARD_SUPPLY_MAPPINGS, CARD_UNIT_MAPPINGS, SUB_UNIT_MAPPINGS
)
load_dotenv()
def get_api_keys():
    """Get API keys from environment variables"""
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    deepl_api_key = os.getenv('DEEPL_API_KEY')
    return deepseek_api_key, deepl_api_key


import re
from datetime import datetime, timedelta


EVENT_CARDS_URL = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/eventCards.json"
EVENT_DECK_BONUSES_URL = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/eventDeckBonuses.json"

def transform_diff(card_diff: List[Dict], mode: str) -> List[Dict]:
    transformed_cards = []  
    
    for  cards in card_diff:
        transformed_card = transform_card(cards, mode) 
        transformed_cards.append(transformed_card)    

    return transformed_cards 

def transform_card(card_data, mode):
    card_id = card_data.get('id', 0)
    character = get_character_name(card_data.get('characterId', 0))
    unit = get_unit_name(character)
    char_id = get_character_id(character, unit, card_id)
    jp_prefix = card_data.get("prefix", "")

    card_rarity = convert_rarity(card_data.get("cardRarityType", "rarity_1"))
    if card_rarity == 5:
        initial_name = get_birthday_card_name(jp_prefix)
    else:
        translated_name = translate_jp_to_en(jp_prefix)
        initial_name = translated_name if translated_name else ""
    
    card_type = convert_card_type(card_data.get("cardSupplyId", 1))
    if card_type == "limited_collab":
        en_release_time = 0
        initial_name = ""

    if mode == "jp":
        jp_release_time = card_data.get("releaseAt", 0)
        en_release_time = calculate_en_release_time(jp_release_time)
        new_card = {
            "id": card_id,
            "name": initial_name,
            "jp_name": jp_prefix,
            "attribute": capitalize_attr(card_data.get("attr", "")),
            "rarity": card_rarity,
            "card_type": card_type,
            "jp_released": jp_release_time,
            "en_released": en_release_time,
            "charId": char_id,
            "character": character,
            "unit": unit,
        }
            # sub_unit for VS
        if unit == "Virtual Singers" and card_type != "limited_collab":
            if char_id >= 27:
                sub_unit = get_sub_unit(card_id)
                if sub_unit:
                    new_card["sub_unit"] = sub_unit

    elif mode =="en":
        new_card = {
            "id":card_data.get("id",0),
            "name": card_data.get("prefix", 0),
            "en_released": card_data.get("releaseAt",0)
        }
    
    return new_card
  

def update_en_cards(my_cards, en_cards_diff):
    keys_to_update = ["id","name","en_released"] 
    en_cards_diff_dict = {obj['id']: obj for obj in en_cards_diff if 'id' in obj}
    updated_count = 0
    
    for obj1 in my_cards:
        obj1_id = obj1.get('id')
        
        if obj1_id in en_cards_diff_dict:
            obj2 = en_cards_diff_dict[obj1_id]
            
            # Check if any of the specific keys have different values
            needs_update = False
            changes = []
            
            for key in keys_to_update:
                if key in obj2 and obj1.get(key) != obj2[key]:
                    obj1[key] = obj2[key]
                    needs_update = True
                    changes.append(f"{key}: {obj1.get(key)} -> {obj2[key]}")
            
            if needs_update:
                updated_count += 1
                print(f"ID {obj1_id} updated. Changes: {', '.join(changes)}")
    
    print(f"Updated {updated_count} objects")
    return my_cards






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
        events = fetch_json_from_url("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/events.json")
        cards = fetch_json_from_url("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/cards.json")
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
            # For mixed events
            if event.get("unit") == "none":
                for ev in event_cards:
                    if ev.get("eventId") == event_id and ev.get("bonusRate") == 20:
                        for card in cards:
                            if ev.get("cardId") == card.get("id"):
                                character = get_character_name(card.get('characterId'))
                                unit = get_unit_name(character)
                                event_unit = unit
                           
                                return event_unit
                            
            elif event.get("id") == event_id:
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

    print("Getting Virtual Singer ID...")
    try:
        # Fetch the required JSON files
        event_cards = fetch_json_from_url(EVENT_CARDS_URL)
        event_deck_bonuses = fetch_json_from_url(EVENT_DECK_BONUSES_URL)
        
        # Step 1: Find matching event card by cardId
        matching_event_card = None
        for event_card in event_cards:
            if event_card.get("cardId") == card_id:
                matching_event_card = event_card
                print(matching_event_card)
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
                if len(matching_bonuses) == 6:
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
    

  
    try:
   
        return CHARACTERS.index(character_name) + 1
    except ValueError:
        return 0 


