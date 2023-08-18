from datetime import datetime, timedelta


def convert_to_utc(days_since_zero):
    # Define the reference date
    reference_date = datetime(1, 1, 1)

    # Calculate the timdelta for both values
    first_time_delta = timedelta(days=days_since_zero)

    # Calculate the UTC datetimes
    first_utc_datetime = reference_date + first_time_delta

    return first_utc_datetime
