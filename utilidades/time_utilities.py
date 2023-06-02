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


def calculate_age(birth_date):
    current_date = datetime.now().date()
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    age = current_date.year - birth_date.year

    # Adjust age if the birth month and day haven't occurred yet
    if current_date.month < birth_date.month or (current_date.month == birth_date.month and current_date.day < birth_date.day):
        age -= 1

    return age
