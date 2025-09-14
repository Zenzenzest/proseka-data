import json
import requests
import pytz
from datetime import datetime, timedelta
from typing import Dict, List
from .common_transform import get_pst_pdt_status
from .mappings import EVENT_UNIT_MAPPINGS

def fetch_json_from_url(url: str) -> List[Dict]:
    """Fetch JSON data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def update_en_events_from_en_source(en_events_data: List[Dict], existing_en_events: List[Dict]) -> List[Dict]:
    """Update EN events from EN source data"""

    en_event_lookup = {event.get("id"): event for event in existing_en_events}
    
    # only process ID >= 140
    events_to_process = [event for event in en_events_data if event.get("id", 0) >= 140]
    
    updated_count = 0
    updated_event_ids = []
    result_events = existing_en_events.copy()
 
    for en_source_event in events_to_process:
        event_id = en_source_event.get("id")
   
        if event_id in en_event_lookup:
            for i, event in enumerate(result_events):
                if event.get("id") == event_id:
                    original_event = event.copy()
                    
                    # Update fields if they're different
                    en_name = en_source_event.get("name", "")
                    en_start = en_source_event.get("startAt", 0)
                    en_end = en_source_event.get("aggregateAt", 0)
                    en_close = en_source_event.get("closedAt", 0)
                    
                    if result_events[i].get("name") != en_name:
                        result_events[i]["name"] = en_name
                    
                    if result_events[i].get("start") != en_start:
                        result_events[i]["start"] = en_start
                    
                    if result_events[i].get("end") != en_end:
                        result_events[i]["end"] = en_end
                    
                    if result_events[i].get("close") != en_close:
                        result_events[i]["close"] = en_close
                    
                    if result_events[i] != original_event:
                        updated_count += 1
                        updated_event_ids.append(event_id)
                    break
    
    if updated_count > 0:
        print(f"Updated {updated_count} EN events from EN source")
        print(f"Updated event IDs: {updated_event_ids}")
    
    return result_events


def adjust_time_for_en(jp_time_ms: int) -> int:
    """Add 1 year and timezone hours to JP time for EN timing"""
    if jp_time_ms == 0:
        return 0
    

    jp_dt = datetime.fromtimestamp(jp_time_ms / 1000, tz=pytz.UTC)
    

    en_dt = jp_dt.replace(year=jp_dt.year + 1)
    

    additional_hours = 16 if get_pst_pdt_status() == "PDT" else 17
    en_dt = en_dt + timedelta(hours=additional_hours)
    

    return int(en_dt.timestamp() * 1000)

def get_event_cards(event_id: int, event_cards_data: List[Dict]) -> List[int]:
    """Get card IDs for an event from eventCards data"""
    card_ids = []
    for event_card in event_cards_data:
        if event_card.get("eventId") == event_id:
            card_id = event_card.get("cardId")
            if card_id:
                card_ids.append(card_id)
    return sorted(card_ids)

def transform_jp_events(jp_events_data: List[Dict], existing_jp_events: List[Dict], event_cards_data: List[Dict]) -> List[Dict]:
    """Transform JP events data to our format"""
    result = []
    
  
    existing_event_lookup = {event.get("id"): event for event in existing_jp_events}
    

    for jp_event in jp_events_data:
        event_id = jp_event.get("id")
        
        # Skip if event already exists
        if event_id in existing_event_lookup:
            continue
            

        name = jp_event.get("name", "")
        start_time = jp_event.get("startAt", 0)
        end_time = jp_event.get("aggregateAt", 0)
        close_time = jp_event.get("closedAt", 0)
        unit = EVENT_UNIT_MAPPINGS.get(jp_event.get("unit", ""), "")
        event_type = jp_event.get("eventType", "")
        cards = get_event_cards(event_id, event_cards_data)
        
        # JP event object
        jp_event_obj = {
            "id": event_id,
            "name": name,
            "start": start_time,
            "end": end_time,
            "close": close_time,
            "unit": unit,
            "cards": cards,
            "keywords": [],
            "event_type": event_type,
            "type": ""
        }
        
        result.append(jp_event_obj)
    
    return result

def create_en_event_from_jp(jp_event: Dict, event_cards_data: List[Dict]) -> Dict:
    """Create EN event from JP event with timezone-adjusted timing"""

    event_id = jp_event.get("id")
    name = jp_event.get("name", "")
    jp_start_time = jp_event.get("start")
    jp_end_time = jp_event.get("end")
    jp_close_time = jp_event.get("close")
    unit = jp_event.get("unit", "")
    event_type = jp_event.get("event_type", "")
    cards = jp_event.get("cards", [])
    
    # Adjust time for EN
    en_start_time = adjust_time_for_en(jp_start_time)
    en_end_time = adjust_time_for_en(jp_end_time)
    en_close_time = adjust_time_for_en(jp_close_time)
    
    # EN event object 
    en_event = {
        "id": event_id,
        "name": name,
        "start": en_start_time,
        "end": en_end_time,
        "close": en_close_time,
        "unit": unit,
        "cards": cards,
        "keywords": [],
        "event_type": event_type,
        "type": ""
    }
    
    return en_event