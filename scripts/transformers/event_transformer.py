import json
import requests
import re
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


def update_event_ids(transformed_diff: List[Dict], banners: List[Dict]) -> List[Dict]:

    event_sets = []
    for event in transformed_diff:
        cards = set(event.get('cards', []))
        event_sets.append((event, cards))

    for banner in reversed(banners):
        banner_cards = set(banner.get("cards", []))

        for ev, event_cards in event_sets:
            common_cards = len(banner_cards & event_cards)
            if common_cards >= 3:
                banner["event_id"] = ev.get("id")
                banner["keywords"] = ev.get("keywords")

    return banners


def update_en_events(en_diff: List[Dict], en_events: List[Dict]) -> List[Dict]:
    lookup = {ev['id']: ev for ev in en_diff}

    for event in en_events:
        if event["id"] in lookup:
            print(f"Processing Event: {event['id']}")
            for key, value in lookup[event["id"]].items():
                if key == "name":
                    event["name"] = value
                elif key == "startAt":
                    event["start"] = value
                elif key == "aggregateAt":
                    event["end"] = value
                elif key == "closedAt":
                    event["close"] = value

    return en_events


def transform_events(jp_diff: List[Dict], events: List[Dict], jp_cards: List[Dict], mode: str) -> List[Dict]:
    event_cards = fetch_json_from_url(
        "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/refs/heads/main/eventCards.json")

    events_diff = []

    for event in jp_diff:
        id = event.get("id")
        name = event.get("name")
        unit = EVENT_UNIT_MAPPINGS.get(event.get("unit"))
        cards = get_event_cards(id, event_cards)
        start = event.get("startAt")
        end = event.get("aggregateAt")
        close = event.get("closedAt")
        event_type = event.get("eventType")
        keywords = []

        new_event = {
            "id": id,
            "name": name,
            "unit": unit,
            "cards": cards,
            "start": start,
            "end": end,
            "close": close,
            "event_type": event_type,
            "keywords": keywords
        }

        # Auto increment from the last focus event
        # Tsukasa 6th Focus Event -> Tsukasa 7th Focus Event
        # Won't work if there's wl3 event. too lazy to add a fallback
        if unit != "mixed":

            first_card_id = cards[0]
            card_data = next(
                (card for card in jp_cards if card["id"] == first_card_id), None)
            character = card_data.get("character", "")
            parts = character.split(" ")
            first_name = parts[1]
            # Find the previous focus event

            for ev in reversed(events):
                if first_name in ev.get("type", ""):
                    print(ev["type"])
                    focus = increment_focus_event_type(ev["type"])
                    kw = ev.get("keywords")
                    new_event["type"] = focus
                    new_event["keywords"] = increment_keywords(kw)
                    break

        elif unit == "mixed":
            new_event["type"] = "Mixed Event"

        if mode == "jp":
            events_diff.append(new_event)

        elif mode == "en":
            new_event["start"] = adjust_time_for_en(start)
            new_event["end"] = adjust_time_for_en(end)
            new_event["close"] = adjust_time_for_en(close)
            events_diff.append(new_event)

    return events_diff


def adjust_time_for_en(jp_time_ms: int) -> int:
    """Add 1 year and timezone hours to JP time for EN timing"""
    if jp_time_ms == 0:
        return 0
    jp_dt = datetime.fromtimestamp(jp_time_ms / 1000, tz=pytz.UTC)

    en_dt = jp_dt.replace(year=jp_dt.year + 1)

    additional_hours = 16 if get_pst_pdt_status() == "PDT" else 17
    en_dt = en_dt + timedelta(hours=additional_hours)

    return int(en_dt.timestamp() * 1000)


def increment_focus_event_type(text):
    def increment_match(match):
        number = int(match.group(1))
        return f"{number + 1}{match.group(2)}"

    return re.sub(r'(\d+)(st|nd|rd|th)', increment_match, text)


def increment_keywords(keywords: List[str]) -> List[str]:
    updated = []
    for word in keywords:
        match = re.match(r"([a-zA-Z]+)(\d+)$", word)
        if match:
            name, num = match.groups()
            new_word = f"{name}{int(num) + 1}"
            updated.append(new_word)
        else:
            updated.append(word)
    return updated


def get_event_cards(event_id: int, event_cards_data: List[Dict]) -> List[int]:
    """Get card IDs for an event from eventCards data"""
    card_ids = []
    for event_card in event_cards_data:
        if event_card.get("eventId") == event_id and event_card.get("isDisplayCardStory") == True:
            card_id = event_card.get("cardId")
            if card_id:
                card_ids.append(card_id)
    return sorted(card_ids)


