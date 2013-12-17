import csv
from django.contrib.gis.geos import Point
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime
import sys
from kv1.models import Kv1Line, Kv1Stop, Kv1Journey, Kv1JourneyStop, Kv1JourneyDate


class Command(BaseCommand):
    """
    Import data exports from the RID database
    """
    folder = ""

    def handle(self, *args, **options):
        self.folder = args[0]
        print "STEP 1: Lines"
        stops = self.do_lines()
        self.log("Got %s stops to process in next step" % len(stops))
        print "==========================\n\nSTEP 2: Stops"
        self.do_stops(stops)


    def do_lines(self):
        stops = []
        with open(self.folder+'/openebs_lines.csv') as routes_file:
            routes_reader = csv.DictReader(routes_file, delimiter=',', quotechar='"')
            for row in routes_reader:
                linenumber = row['operator_id'].split(':')
                lines = Kv1Line.objects.filter(dataownercode=linenumber[0], lineplanningnumber=linenumber[1])
                if lines.count() == 1:
                    line = lines[0]
                    line.headsign = row['name']
                    line.publiclinenumber = row['publiccode']
                    line.save()
                    for line_row in line.stop_map:
                        if 'left' in line_row and line_row['left'] is not None:
                            left = line_row['left']['id'].replace('_', ':')
                            if left not in stops:
                                stops.append(left)
                        if 'right' in line_row and line_row['right'] is not None:
                            right = line_row['right']['id'].replace('_', ':')
                            if right not in stops:
                                stops.append(right)
                else:
                    self.log("Failed to match route: %s" % row['operator_id'])

        return stops

    def do_stops(self, stops):
        with open(self.folder+'/openebs_stops.csv') as stops_file:
           stop_reader = csv.DictReader(stops_file, delimiter=',', quotechar='"')
           i = 0
           for row in stop_reader:
               if row['operator_id'] in stops:
                   stop_code = row['operator_id'].split(':')
                   if Kv1Stop.objects.filter(dataownercode=stop_code[0], userstopcode=stop_code[1]).count() == 0:
                       s = Kv1Stop()
                       s.dataownercode = stop_code[0]
                       s.userstopcode = stop_code[1]
                       s.name = row['name']
                       s.location = Point(float(row['longitude']), float(row['latitude']), srid=4326)
                       s.save()
               i = i+1
               if i % 100 == 0:
                   self.log("Did %s stops" % i)

    def log(self, text):
        print "%s - import_rid: %s" % (datetime.now().isoformat(), text)