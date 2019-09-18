from datetime import date, datetime

def to_json(obj):
    if isinstance(obj, datetime):
        return datetime.timestamp(obj)
    elif isinstance(obj, date):
        return obj.__str__()
    else:
        return obj

def to_readable(obj):
    if obj is None or obj == '':
        return 'N/D'
    elif isinstance(obj, datetime):
        return obj.strftime('%Y/%m/%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.__str__()
    else:
        return obj
