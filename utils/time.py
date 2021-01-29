from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings


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
