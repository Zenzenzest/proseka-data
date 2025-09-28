import os
import json
import requests
import re
from typing import Dict, List, Optional
from .mappings import CHARACTERS, UNIT_PREMIUM
import pytz
from datetime import datetime, timedelta
from .common_transform import get_pst_pdt_status, fetch_json_from_url




# HANDLE en_banners.json

def convert_jp_time_to_en_rerun(jp_start_time: int, jp_end_time: int) -> tuple:
    """Convert JP time to EN rerun time"""
    if jp_start_time == 0 or jp_end_time == 0:
        return 0, 0, 0, 0
    jp_start_dt = datetime.fromtimestamp(jp_start_time / 1000, tz=pytz.UTC)
    
    # Add 1 year 
    en_start_dt = jp_start_dt.replace(year=jp_start_dt.year + 1)
    
    # Get the last day of that month 
    if en_start_dt.month == 12:
        next_month = en_start_dt.replace(year=en_start_dt.year + 1, month=1, day=1)
    else:
        next_month = en_start_dt.replace(month=en_start_dt.month + 1, day=1)
    
    #  12:00 PM GMT+8
    last_day = next_month - timedelta(days=1)
    gmt8 = pytz.timezone('Asia/Shanghai')  # GMT+8
    
    # Create completely naive datetime (no timezone info)
    naive_dt = datetime(
        year=last_day.year,
        month=last_day.month,
        day=last_day.day,
        hour=12,
        minute=0,
        second=0,
        microsecond=0
    )
    en_end_dt = gmt8.localize(naive_dt)
    # Convert to UTC 
    en_end_dt = en_end_dt.astimezone(pytz.UTC)
    en_start_dt = en_end_dt
    # erun array calculations
    #add 1 year and substract 5 days for start date
    rerun_start_dt = jp_start_dt.replace(year=jp_start_dt.year + 1) - timedelta(days=5)
    rerun_start_ms = int(rerun_start_dt.timestamp() * 1000)
    
    # add 1 year and 5 days for end date
    jp_end_dt = datetime.fromtimestamp(jp_end_time / 1000, tz=pytz.UTC)
    rerun_end_dt = jp_end_dt.replace(year=jp_end_dt.year + 1) + timedelta(days=5)
    rerun_end_ms = int(rerun_end_dt.timestamp() * 1000)
    
    # Convert back to milliseconds
    en_start_ms = int(en_start_dt.timestamp() * 1000)
    en_end_ms = int(en_end_dt.timestamp() * 1000)
    
    return en_start_ms, en_end_ms, rerun_start_ms, rerun_end_ms


def convert_jp_time_to_en_normal(jp_start_time: int, jp_end_time: int) -> tuple:
    """Convert JP time to EN normal time (add 1 year + timezone hours)"""
    if jp_start_time == 0 or jp_end_time == 0:
        return 0, 0
    
    # convert to datetime
    jp_start_dt = datetime.fromtimestamp(jp_start_time / 1000, tz=pytz.UTC)
    jp_end_dt = datetime.fromtimestamp(jp_end_time / 1000, tz=pytz.UTC)
    
    # Add 1 year
    en_start_dt = jp_start_dt.replace(year=jp_start_dt.year + 1)
    en_end_dt = jp_end_dt.replace(year=jp_end_dt.year + 1)
    
    # additional hours based on current timezone
    timezone = get_pst_pdt_status()
    additional_hours = 16 if timezone == "PDT" else 17
    en_start_dt = en_start_dt + timedelta(hours=additional_hours)
    en_end_dt = en_end_dt + timedelta(hours=additional_hours)
    # convert back to milliseconds
    en_start_ms = int(en_start_dt.timestamp() * 1000)
    en_end_ms = int(en_end_dt.timestamp() * 1000)
    return en_start_ms, en_end_ms



def create_en_banner_from_jp(jp_banner: Dict, existing_en_banners: List[Dict], jp_banners: List[Dict]) -> Dict:
    jp_banner_copy = jp_banner.copy()
    if jp_banner_copy.get("banner_type") == "Collab":
        return False
    en_banner = {
        "id": get_next_id(existing_en_banners),
        "name": jp_banner_copy.get("name", ""),
        "cards": jp_banner_copy.get("cards", []),
        "characters": jp_banner_copy.get("characters", []),
        "keywords": jp_banner_copy.get("keywords", []),
        "sekai_id": jp_banner_copy.get("sekai_id"),
        "gachaDetails": jp_banner_copy.get("gachaDetails", []),
        "banner_type": jp_banner_copy.get("banner_type", ""),
        "start": 0,
        "end": 0
    }
    
    # special handling for Birthday banners
    if jp_banner_copy.get("banner_type") == "Birthday":
        # find previous birthday banner name and increment year
        cards = jp_banner_copy.get("cards", [])
        previous_name = find_previous_birthday_banner_name(cards, existing_en_banners)
        if previous_name:
            en_banner["name"] = previous_name
        
        # handle start/end times for birthday banners (add 1 year + timezone hours)
        jp_start = jp_banner_copy.get("start", 0)
        jp_end = jp_banner_copy.get("end", 0)
        
        en_start, en_end = convert_jp_time_to_en_normal(jp_start, jp_end)
        en_banner["start"] = en_start
        en_banner["end"] = en_end
    
    # special handling for Limited Event Rerun
    elif jp_banner_copy.get("banner_type") == "Limited Event Rerun":
        jp_start = jp_banner_copy.get("start", 0)
        jp_end = jp_banner_copy.get("end", 0)
        en_start, en_end, rerun_start, rerun_end = convert_jp_time_to_en_rerun(jp_start, jp_end)
        en_banner["start"] = en_start
        en_banner["end"] = en_end
        
        # special rerun fields (only for rerun banners)
        en_banner["type"] = "rerun_estimation"
        en_banner["rerun"] = [rerun_start, rerun_end]
        
        # update name
        original_name = find_original_limited_event_name(
            jp_banner_copy.get("cards", []), 
            existing_en_banners, 
            jp_banners
        )
        if original_name:
            en_banner["name"] = original_name
    else:
        # For non-rerun banners, convert times with timezone adjustment
        jp_start = jp_banner_copy.get("start", 0)
        jp_end = jp_banner_copy.get("end", 0)
        en_start, en_end = convert_jp_time_to_en_normal(jp_start, jp_end)
        
        # Update time fields
        en_banner["start"] = en_start
        en_banner["end"] = en_end
    
    return en_banner


def update_jp_banners_with_en_ids(jp_banners: List[Dict], en_banners: List[Dict]) -> List[Dict]:
    """Update JP banners with en_id from matching EN banners, handling reruns by timing"""
    
   
    en_banners_by_sekai_id = {}
    for en_banner in en_banners:
        sekai_id = en_banner.get("sekai_id")
        if sekai_id not in en_banners_by_sekai_id:
            en_banners_by_sekai_id[sekai_id] = []
        en_banners_by_sekai_id[sekai_id].append(en_banner)
    

    jp_banners_by_sekai_id = {}
    for jp_banner in jp_banners:
        sekai_id = jp_banner.get("sekai_id")
        if sekai_id not in jp_banners_by_sekai_id:
            jp_banners_by_sekai_id[sekai_id] = []
        jp_banners_by_sekai_id[sekai_id].append(jp_banner)
    
    # Track which en_ids have been assigned to prevent duplicates
    assigned_en_ids = set()
    updated_jp_banners = []
    
    # Process each group of banners
    for sekai_id, jp_banner_group in jp_banners_by_sekai_id.items():
        en_banner_group = en_banners_by_sekai_id.get(sekai_id, [])
        
        if not en_banner_group:
            # No matching EN banners, keep original en_id
            updated_jp_banners.extend(jp_banner_group)
        elif len(en_banner_group) == 1:
            en_id = en_banner_group[0].get("id", 0)
            if en_id not in assigned_en_ids:
                assigned_en_ids.add(en_id)
                for jp_banner in jp_banner_group:
                    jp_banner_copy = jp_banner.copy()
                    jp_banner_copy["en_id"] = en_id
                    updated_jp_banners.append(jp_banner_copy)
            else:
                # en_id already assigned, keep original or set to 0
                for jp_banner in jp_banner_group:
                    jp_banner_copy = jp_banner.copy()
                    jp_banner_copy["en_id"] = jp_banner_copy.get("en_id", 0)
                    updated_jp_banners.append(jp_banner_copy)
        else:
            # Multiple EN banners (reruns) - match by timing
            # Create list of (en_banner, is_assigned) to track assignments
            en_banner_assignments = [(en_banner, en_banner.get("id", 0) in assigned_en_ids) 
                                   for en_banner in en_banner_group]
            
            for jp_banner in jp_banner_group:
                jp_banner_copy = jp_banner.copy()
                jp_start = jp_banner.get("start", 0)
                
                best_match = None
                best_time_diff = float('inf')
                

                for en_banner, is_assigned in en_banner_assignments:
                    if not is_assigned:  # Only consider unassigned EN banners
                        en_start = en_banner.get("start", 0)
                        if jp_start > 0 and en_start > 0:
                            # Calculate time difference in days
                            time_diff_ms = abs(en_start - jp_start)
                            time_diff_days = time_diff_ms / (1000 * 60 * 60 * 24)
                            
                            # Check if it's in the expected rerun range
                            if 350 <= time_diff_days <= 380:
                                if time_diff_days < best_time_diff:
                                    best_time_diff = time_diff_days
                                    best_match = en_banner
                
                # Assign en_id based on best match
                if best_match:
                    en_id = best_match.get("id", 0)
                    assigned_en_ids.add(en_id)
                    # Mark this EN banner as assigned
                    for i, (en_banner, is_assigned) in enumerate(en_banner_assignments):
                        if en_banner == best_match:
                            en_banner_assignments[i] = (en_banner, True)
                            break
                    jp_banner_copy["en_id"] = en_id
                else:
                    # use first unassigned EN banner, or set to 0 if all assigned
                    en_id = 0
                    for en_banner, is_assigned in en_banner_assignments:
                        if not is_assigned:
                            en_id = en_banner.get("id", 0)
                            assigned_en_ids.add(en_id)
                            # Mark as assigned
                            for i, (eb, is_a) in enumerate(en_banner_assignments):
                                if eb == en_banner:
                                    en_banner_assignments[i] = (eb, True)
                                    break
                            break
                    jp_banner_copy["en_id"] = en_id
                
                updated_jp_banners.append(jp_banner_copy)
    
    return updated_jp_banners


def find_original_limited_event_name(cards: List[int], existing_en_banners: List[Dict], jp_banners: List[Dict]) -> str:

    if not cards:
        return ""
    first_card_id = cards[0]
    for banner in existing_en_banners:
        if first_card_id in banner.get("cards", []):
            if banner.get("banner_type") == "Limited Event":
                original_name = banner.get("name", "")
                return f"[Rerun] {original_name}"
    for banner in jp_banners:
        if first_card_id in banner.get("cards", []):
            if banner.get("banner_type") == "Limited Event":
                original_name = banner.get("name", "")
                return f"[Rerun] {original_name}"
    
    return ""


def find_previous_birthday_banner_name(cards: List[int], existing_en_banners: List[Dict]) -> str:
    if not cards or len(cards) < 2:
        return ""
    
    #cards except the first one (latest card)
    previous_cards = cards[1:]
    if not previous_cards:
        return ""
    
    # Look for matching birthday banner in existing EN banners
    for banner in existing_en_banners:
        if banner.get("banner_type") == "Birthday":
            banner_cards = banner.get("cards", [])
    
            if set(previous_cards).issubset(set(banner_cards)) or set(previous_cards) == set(banner_cards):
                previous_name = banner.get("name", "")
                if previous_name:
                    # Look for 4-digit year pattern and increment it
                    import re
                    year_pattern = r'(\d{4})'
                    match = re.search(year_pattern, previous_name)
                    if match:
                        current_year = int(match.group(1))
                        next_year = current_year + 1
                        # Replace the year in the name
                        return re.sub(year_pattern, str(next_year), previous_name)
                    return previous_name
    
    return ""




# UPDATE FROM EN BANNERS
def normalize_rerun_name(name: str) -> str:
    """Normalize rerun names by removing [Rerun] and [It's Back] prefixes"""
    if name.startswith("[Rerun] "):
        return name[8:]  
    elif name.startswith("[It's Back] "):
        return name[12:] 
    return name


def update_en_banners_from_en_source(en_gachas: List[Dict], existing_en_banners: List[Dict], en_gachas_changes: List[Dict] = None) -> List[Dict]:
    """Update EN banners from EN source data - now supports adding new entries"""
    cards_data = []
    if os.path.exists('cards.json'):
        with open('cards.json', 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
    en_banner_lookup = {banner.get("sekai_id"): banner for banner in existing_en_banners}
    
    # Determine which gachas to process
    if en_gachas_changes:
        # Process only the changed gachas (incremental update)
        gachas_to_process = [gacha for gacha in en_gachas_changes if gacha.get("id", 0) > 570]
        print(f"Processing {len(gachas_to_process)} changed EN gachas")
    else:
        # Fallback to original behavior - process all gachas above 570
        gachas_to_process = [gacha for gacha in en_gachas if gacha.get("id", 0) > 570]
        print(f"Processing all EN gachas above ID 570")
    
    updated_count = 0
    added_count = 0
    updated_banner_ids = []
    added_banner_ids = []
    result_banners = existing_en_banners.copy()
    
    # Track which sekai_ids are processed to avoid duplicates
    processed_sekai_ids = set()
    
    # Process each gacha
    for gacha in gachas_to_process:
        if "3★" in gacha.get("name"):
            continue
        sekai_id = gacha.get("id")
        
        # Skip if already processed (avoid duplicates)
        if sekai_id in processed_sekai_ids:
            continue
        processed_sekai_ids.add(sekai_id)

        name = gacha.get("name", "")

        gacha_pickups = gacha.get("gachaPickups", [])
        card_ids = extract_card_ids(gacha_pickups)
        banner_type = determine_banner_type(name, card_ids, cards_data)
        gacha_details_card_ids = extract_rarity_4_card_ids(gacha.get("gachaDetails", []), cards_data, banner_type)

        # Check if this banner already exists
        if sekai_id in en_banner_lookup:
            # UPDATE existing banner
            for i, banner in enumerate(result_banners):
                if banner.get("sekai_id") == sekai_id:
                    existing_banner = banner.copy()
                    original_banner = existing_banner.copy()
                    
                    # Update fields if different
                    en_name = gacha.get("name", "")
                    en_start = gacha.get("startAt", 0)
                    en_end = gacha.get("endAt", 0)
                    en_gacha_details = gacha_details_card_ids


                    existing_name = existing_banner.get("name", "")
                    if normalize_rerun_name(existing_name) != normalize_rerun_name(en_name):
                        result_banners[i]["name"] = en_name
                        
                    if result_banners[i].get("start") != en_start:
                        result_banners[i]["start"] = en_start
                        
                    if result_banners[i].get("end") != en_end:
                        result_banners[i]["end"] = en_end
                    
                    if result_banners[i].get("gachaDetails") != en_gacha_details:
                        result_banners[i]["gachaDetails"] = en_gacha_details
                        
                    # Check if banner was actually modified
                    if result_banners[i] != original_banner:
                        updated_count += 1
                        banner_id = result_banners[i].get("id", "Unknown")
                        updated_banner_ids.append(banner_id)
                    break
        else:
            # ADD new banner 
            new_banner = {
                "id": get_next_id(result_banners),
                "sekai_id": sekai_id,
                "name": name,
                "characters": get_character_ids_from_cards(card_ids, cards_data, CHARACTERS),
                "start": gacha.get("startAt", 0),
                "end": gacha.get("endAt", 0),
                "cards": card_ids, 
                "keywords": [],
                "gachaDetails": gacha_details_card_ids,
                "banner_type": banner_type,
            }
            
            result_banners.append(new_banner)
            added_count += 1
            added_banner_ids.append(new_banner["id"])
    
    # Print summary
    if updated_count > 0 or added_count > 0:
        summary = []
        if updated_count > 0:
            summary.append(f"Updated {updated_count} EN banners")
        if added_count > 0:
            summary.append(f"Added {added_count} new EN banners")
        print(", ".join(summary))
        
        if updated_banner_ids:
            print(f"Updated banner IDs: {updated_banner_ids}")
        if added_banner_ids:
            print(f"Added banner IDs: {added_banner_ids}")
    
    return result_banners










def extract_rarity_4_card_ids(gacha_details: List[Dict], cards_data: List[Dict], banner_type: str) -> List[int]:
    # return empty array if bday
    if banner_type == "Birthday":
        return []
    rarity_4_card_ids = []
    card_lookup = {card.get("id"): card for card in cards_data}
    
    # process each ganner detail
    for detail in gacha_details:
        card_id = detail.get("cardId")
        if card_id:
            # Look up the card in cards.json
            card = card_lookup.get(card_id)
            if card:
   
                if card.get("rarity") == 4 or card.get("card_type") == "limited_collab":
                    rarity_4_card_ids.append(card_id)
    
    return rarity_4_card_ids


def get_character_ids_from_cards(card_ids: List[int], cards_data: List[Dict], characters_list: List[str]) -> List[int]:
    character_names = set()  #  set to prevent duplicates
    card_lookup = {card.get("id"): card for card in cards_data}
    
    # unique character names from cards
    for card_id in card_ids:
        card = card_lookup.get(card_id)
        if card:
            character_name = card.get("character")
            if character_name:
                character_names.add(character_name)
    
    # Convert character names to IDs
    character_ids = []
    for character_name in character_names:
        try:
      
            char_id = characters_list.index(character_name) + 1
            character_ids.append(char_id)
        except ValueError:
    
            continue
    return sorted(character_ids)

def get_next_id(existing_banners: List[Dict]) -> int:
    if not existing_banners:
        return 1
    return max(banner.get("id", 0) for banner in existing_banners) + 1

def extract_card_ids(gacha_pickups: List[Dict]) -> List[int]:
    return [pickup.get("cardId", 0) for pickup in gacha_pickups if pickup.get("cardId")]


def extract_japanese_name(name: str) -> Optional[str]:
    match = re.search(r'(?:\[復刻\])?\[([^\]]+)\]', name)
    return match.group(1) if match else None

def is_birthday_banner(name: str) -> bool:
    return "HAPPY BIRTHDAY" in name or "HAPPY ANNIVERSARY" in name

def group_birthday_banners(gachas: List[Dict]) -> List[Dict]:
    birthday_gachas = [g for g in gachas if g.get("id", 0) >= 800 and is_birthday_banner(g.get("name", ""))]
    
    # Group by Japanese name
    grouped = {}
    for gacha in birthday_gachas:
        jp_name = extract_japanese_name(gacha.get("name", ""))
        if jp_name:
            if jp_name not in grouped:
                grouped[jp_name] = []
            grouped[jp_name].append(gacha)
    
    # For each group, keep only the first banner but combine all cards
    result = []
    processed_ids = set()
    
    for jp_name, banners in grouped.items():
        if banners:
            # sort by ID to ensure we get the first one
            banners.sort(key=lambda x: x.get("id", 0))
            first_banner = banners[0].copy()
            
            # Collect all card IDs from all banners in this group
            all_cards = []
            for banner in banners:
                banner_id = banner.get("id")
                if banner_id:
                    processed_ids.add(banner_id)
                card_ids = extract_card_ids(banner.get("gachaPickups", []))
                all_cards.extend(card_ids)
            
            # combined card IDs
            first_banner["gachaPickups"] = [{"cardId": card_id} for card_id in all_cards]
            result.append(first_banner)
   
    for gacha in gachas:
        gacha_id = gacha.get("id", 0)
        if gacha_id >= 800 and gacha_id not in processed_ids:
            result.append(gacha)
    return result


def determine_banner_type(name: str, cards: List[int], cards_data: List[Dict]) -> str:
    # Name-based conditions 
    if "HAPPY BIRTHDAY" in name or "HAPPY ANNIVERSARY" in name:
        return "Birthday"
    elif "10連無料" in name:
        return "Free Pull"
    elif "復刻" in name:
        return "Limited Event Rerun"
    elif "セレクトリスト" in name:
        return "Your Pick"
    elif "メモリアルセレクト" in name:
        return "Memorial Select"
    elif "プレミアムプレゼント" in name or "Premium Gift" in name:
   
        for unit in UNIT_PREMIUM:
            if unit in name:
                return "Unit Premium Gift"
        return "Premium Gift"
    
    # Card-based conditions
    if cards and len(cards) >= 3 and cards_data:
        # Get first 3 cards and check their types
        first_three_card_ids = cards[:3]
        first_three_cards = []
        
        # Find card data for first 3 cards
        card_lookup = {card.get("id"): card for card in cards_data}
        for card_id in first_three_card_ids:
            card_data = card_lookup.get(card_id)
            if card_data:
                first_three_cards.append(card_data)

        if len(first_three_cards) == 3:
            card_types = [card.get("card_type", "") for card in first_three_cards]
            
            # All must be same type
            if len(set(card_types)) == 1:  
                first_type = card_types[0]
                if first_type == "limited":
                    return "Limited Event"
                elif first_type == "permanent":
                    return "Event"
                elif first_type == "unit_limited":
                    return "Unit Limited Event"
                elif first_type == "bloom_fes":
                    return "bloom_fes"
                elif first_type == "limited_collab":
                    return "Collab"
                

    
    # Default banner type
    return "Event"


def transform_jp_banners(jp_gachas: List[Dict], existing_banners: List[Dict], cards_data: List[Dict]) -> List[Dict]:
    """Transform JP gachas to banner format"""
    result = []

    existing_banner_lookup = {banner.get("sekai_id"): banner for banner in existing_banners}
    
    # group birthday banners
    processed_gachas = group_birthday_banners(jp_gachas)
    
    # Filter gachas to only process those with ID 800 and above
    gachas_to_process = [gacha for gacha in processed_gachas if gacha.get("id", 0) >= 800]
    
    # Process each
    for gacha in gachas_to_process:
        sekai_id = gacha.get("id")
        
        # Skip if this banner already exists in my jp_banners
        if sekai_id in existing_banner_lookup:
            continue
            
        # Extract data from source
        name = gacha.get("name", "")
        start_time = gacha.get("startAt", 0)
        end_time = gacha.get("endAt", 0)
        gacha_pickups = gacha.get("gachaPickups", [])
        
        # Transform 
        card_ids = extract_card_ids(gacha_pickups)
        banner_type = determine_banner_type(name, card_ids, cards_data)
        
        # Get next auto-increment ID
        banner_id = get_next_id(existing_banners + result)

      # extract gachaDetails card IDs (only rarity 4)
        gacha_details_card_ids = extract_rarity_4_card_ids(gacha.get("gachaDetails", []), cards_data, banner_type)

        # Create banner object
        banner = {
            "id": banner_id,
            "name": name,
            "start": start_time,
            "end": end_time,
            "cards": card_ids,
            "en_id": 0,  
            "banner_type": banner_type,
            "characters": get_character_ids_from_cards(card_ids, cards_data, CHARACTERS),
            "keywords": [],   
            "sekai_id": sekai_id,
            "gachaDetails": gacha_details_card_ids
}
        result.append(banner)
    
    return result