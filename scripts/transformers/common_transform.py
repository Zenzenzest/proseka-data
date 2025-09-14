import pytz
from datetime import datetime
from typing import Dict, List
import requests



def get_pst_pdt_status():
    """Determine if current time is PST or PDT"""
    pacific = pytz.timezone('US/Pacific')
    current_time = datetime.now(pacific)
    
    # check if PDT OR PST
    if current_time.dst().total_seconds() != 0:
        return "PDT"
    else:
        return "PST"
    



def fetch_json_from_url(url: str) -> List[Dict]:
    """Fetch JSON data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


