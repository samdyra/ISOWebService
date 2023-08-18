from datetime import datetime, timedelta, timezone


def convert_to_iso8601_with_offset(days_since_zero):
    # Define the reference date
    reference_date = datetime(1, 1, 1)

    # Calculate the timedelta for the given value
    time_delta = timedelta(days=days_since_zero)

    # Calculate the GMT datetime
    gmt_datetime = reference_date + time_delta

    # Convert the GMT datetime to a GMT timezone-aware datetime
    gmt_datetime_gmt = gmt_datetime.replace(tzinfo=timezone.utc)

    # Format the datetime in ISO 8601 with UTC offset
    iso8601_with_offset = gmt_datetime_gmt.strftime('%Y-%m-%dT%H:%M:%S%z')

    return iso8601_with_offset
