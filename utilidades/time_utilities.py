from datetime import datetime, timedelta
import pytz


def get_today():
    timezone = pytz.timezone("US/Eastern")
    utc_time = datetime.utcnow()
    local_time = utc_time + timedelta(hours=-5)
    local_time = timezone.localize(local_time)

    # format the date as Y-M-D
    today_str = local_time.strftime("%Y-%m-%d")
    return today_str
