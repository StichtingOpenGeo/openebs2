import logging
from django.core.management import BaseCommand
from reports.models import SnapshotLog

class Command(BaseCommand):
    log = logging.getLogger('openebs.snapshot')

    def handle(self, *args, **options):
        SnapshotLog.do_snapshot()