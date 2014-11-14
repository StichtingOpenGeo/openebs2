from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings

__author__ = 'joelthuis'

def get_operator_date():
    # TODO - add Dataownercode = parameter for future expansion in case different operators use different values
    current = now()
    if current.hour < settings.CROSSOVER_HOUR:
        current = current - timedelta(days=1)
    return current.date()