from datetime import datetime

def datetime_filter(timestamp, format_string):
    return datetime.fromtimestamp(timestamp).strftime(format_string)