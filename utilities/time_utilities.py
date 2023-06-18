from datetime import datetime, timedelta
import pytz


def get_today():
    """
    Retrieves the current date in the US/Eastern timezone and returns it as a string in the format Y-M-D.

    Returns:
        str: The current date formatted as Y-M-D.
    """
    timezone = pytz.timezone("US/Eastern")
    utc_time = datetime.utcnow()
    local_time = utc_time + timedelta(hours=-5)
    local_time = timezone.localize(local_time)

    # format the date as Y-M-D
    today_str = local_time.strftime("%Y-%m-%d")
    return today_str


def calculate_age(birth_date):
    """
    Calculates the age based on the provided birth date.

    Args:
        birth_date (str): The birth date in the format Y-M-D.

    Returns:
        int: The calculated age.
    """
    current_date = datetime.now().date()
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    age = current_date.year - birth_date.year

    # Adjust age if the birth month and day haven't occurred yet
    if current_date.month < birth_date.month or (
            current_date.month == birth_date.month and current_date.day < birth_date.day):
        age -= 1

    return age
