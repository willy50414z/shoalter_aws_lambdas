from datetime import datetime

DEFAULT_DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'


def ts_to_datetime_str(ts):
    dt = datetime.fromtimestamp(ts)
    return dt.strftime(DEFAULT_DATETIME_FORMAT)


def datetime_str_to_ts(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, DEFAULT_DATETIME_FORMAT)
    return datetime_obj.timestamp()
