import csv

# Hack to disable logging for now
# TODO: test if we can remove this
from django.db import connection, Error

connection.use_debug_cursor = False

from django.contrib.gis.geos import Point
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime
from kv1.models import Kv1Line, Kv1Stop


class Command(BaseCommand):
    """
    Import data exports from the RID database
    """
    folder = ""

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str)

    def handle(self, *args, **options):
        self.folder = options.get('folder', '')
        print("STEP 1: Lines")
        self.do_lines()
        print("==========================\n\nSTEP 2: Stops")
        self.do_stops()

    def do_lines(self):
        with open(self.folder+'/openebs_lines.csv') as routes_file:
            routes_reader = csv.DictReader(routes_file, delimiter=',', quotechar='"')
            for row in routes_reader:
                try:
                    self.do_line(row)
                except Error as error:
                    self.log("Issue parsing line: %s (with row: %s)" % (error, row))

    def do_line(self, row):
        linenumber = row['operator_id'].split(':')
        lines = Kv1Line.objects.filter(dataownercode=linenumber[0], lineplanningnumber=linenumber[1])
        if lines.count() == 1:
            line = lines[0]
            line.headsign = row['name']
            line.publiclinenumber = row['publiccode']
            line.save()
        else:
            self.log("Failed to match route: %s" % row['operator_id'])

    def do_stops(self):
        with open(self.folder+'/openebs_stops.csv') as stops_file:
            stop_reader = csv.DictReader(stops_file, delimiter=',', quotechar='"')
            i = 0
            for row in stop_reader:
                try:
                    self.do_stop(row)
                    i += 1
                    if i % 100 == 0:
                        self.log("Did %s stops" % i)
                except Error as error:
                    self.log("Issue parsing stop: %s (with row: %s)" % (error, row))

    def do_stop(self, row):
        stop_code = row['operator_id'].split(':')
        location = Point(float(row['longitude']), float(row['latitude']), srid=4326)
        s, created = Kv1Stop.objects.get_or_create(dataownercode=stop_code[0], userstopcode=stop_code[1],
                                                   defaults={'location': location})
        s.name = row['name']
        s.location = location
        s.timingpointcode = row['timingpointcode']
        s.save()

    def log(self, text):
        self.stdout.write("%s - import_rid: %s" % (datetime.now().isoformat(), text))
