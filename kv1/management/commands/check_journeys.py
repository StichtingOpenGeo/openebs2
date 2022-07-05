from datetime import datetime, timedelta
from django.core.management import BaseCommand
from kv1.models import Kv1Journey
from django.utils.timezone import make_aware
from django.core.mail import mail_admins


class Command(BaseCommand):
    """
    Check if there are journeys in database for two days from now.
    """

    def handle(self, *args, **options):
        two_days_from_now = make_aware(datetime.now() + timedelta(days=2))
        journey_qry = Kv1Journey.objects.filter(dates__date__gte=two_days_from_now)
        if journey_qry.count() == 0:
            subject = f"Geen nieuwe ritten in database vanaf {datetime.strftime(two_days_from_now, '%d-%m-%Y')}"
            message = f"Er staan geen nieuwe ritten in de database met een datum groter of gelijk aan {datetime.strftime(two_days_from_now, '%d-%m-%Y')}"
            mail_admins(subject, message)
