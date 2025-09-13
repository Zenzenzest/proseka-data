import pytz
from datetime import datetime, timedelta



def get_pst_pdt_status():
    """Determine if current time is PST or PDT"""
    pacific = pytz.timezone('US/Pacific')
    current_time = datetime.now(pacific)
    
    # check if PDT OR PST
    if current_time.dst().total_seconds() != 0:
        return "PDT"
    else:
        return "PST"