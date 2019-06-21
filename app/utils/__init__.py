from datetime import date, datetime

def custom_converter(obj):
    if isinstance(obj, datetime):
        return datetime.timestamp(obj)
    elif isinstance(obj, date):
        return obj.__str__()
    else:
        return obj
