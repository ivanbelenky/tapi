from datetime import datetime

def datetime_parser(dt: datetime):
    return dt.strftime("%Y-%m-%dT%H:%M:00.000Z")
