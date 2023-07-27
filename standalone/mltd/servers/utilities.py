from datetime import datetime, timezone


def format_datetime(dt):
    """Return a str formatted as 'YYYY-MM-DDThh:mm:ss+zzzz'."""
    if not isinstance(dt, datetime):
        raise TypeError('Not a datetime object')
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')


def str_to_datetime(s):
    """Convert a str into a UTC datetime."""
    if not s:
        return None
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)

