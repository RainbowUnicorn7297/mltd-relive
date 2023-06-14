from datetime import datetime


def format_datetime(dt):
    """Return a str formatted as 'YYYY-MM-DDThh:mm:ss+zzzz'."""
    if not isinstance(dt, datetime):
        raise TypeError('Not a datetime object')
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')

