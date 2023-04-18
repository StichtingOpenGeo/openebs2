from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings
from datetime import datetime
from django.utils.timezone import make_aware

def get_operator_date():
    # TODO - add Dataownercode = parameter for future expansion in case different operators use different values
    current = now()
    if current.hour < settings.CROSSOVER_HOUR:
        current = current - timedelta(days=1)
    return current.date()


def get_operator_date_aware():
    # TODO - add Dataownercode = parameter for future expansion in case different operators use different values
    current = now()
    if current.hour < settings.CROSSOVER_HOUR:
        current = current - timedelta(days=1)

    result = current.replace(hour=0, minute=0, second=0, microsecond=0)
    return result


def datetime_32h(operatingday, begintime):
    if begintime is None:
        return None
    else:
        operatingday_time = make_aware(datetime.combine(operatingday, datetime.min.time()))
        begintime_diff = begintime - operatingday_time
        hours = begintime_diff.days * 24 + (begintime_diff.seconds / 3600)
        minutes = (begintime_diff.seconds % 3600) / 60
        seconds = begintime_diff.seconds % 60
        return '%02d:%02d:%02d' % (hours, minutes, seconds)


def seconds_to_hhmm(seconds):
    hours = seconds // (3600)
    seconds %= (3600)
    minutes = seconds // 60
    if hours < 24:
        time = "%02i:%02i" % (hours, minutes)
    else:
        hours -= 24
        time = "%02i:%02i (+1)" % (hours, minutes)
    return time


def hhmm_to_seconds(call, time):
    hour = time.hour
    if call == 'end':
        if time.hour < 4:
            hour = time.hour + 24
    seconds = hour * 3600
    seconds += time.minute * 60
    seconds += time.second

    return seconds
