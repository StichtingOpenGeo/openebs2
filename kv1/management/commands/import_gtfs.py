import csv
from zipfile import ZipFile
from django.contrib.gis.geos import Point
from django.core.management import BaseCommand
import transitfeed
from kv1.models import Kv1Line, Kv1Stop


__author__ = 'joel'

class Command(BaseCommand):

    def handle(self, *args, **options):
        with ZipFile(args[0], 'r') as myzip:
            #print [ f.filename for f in myzip.filelist]
            stops, agency = self.do_routes(myzip)
            self.do_stops(myzip, stops, agency)

    def do_routes(self, myzip):
        stops = []
        agency = []
        with myzip.open('routes.txt') as routes_file:
            routes_reader = csv.DictReader(routes_file, delimiter=',', quotechar='"')
            for row in routes_reader:
                lines = Kv1Line.objects.filter(lineplanningnumber=row['route_short_name'], dataownercode=row['agency_id'])
                if len(lines) > 1:
                    print "Matched more than one"
                elif len(lines) == 1:
                    lines[0].headsign = row['route_long_name']
                    lines[0].save()
                    for row in lines[0].stop_map:
                        if row['left'] is not None:
                            left = row['left']['id'].split('_')[1]
                            if left not in stops:
                                stops.append(left)
                                agency.append(row['left']['id'].split('_')[0])
                        if row['right'] is not None:
                            right = row['right']['id'].split('_')[1]
                            if right not in stops:
                                stops.append(right)
                                agency.append(row['right']['id'].split('_')[0])

                    #print "Matched %s" % (row)

        return (stops, agency)

    def do_stops(self, myzip, stops, agency):
        with myzip.open('stops.txt') as stops_file:
           stop_reader = csv.DictReader(stops_file, delimiter=',', quotechar='"')
           for row in stop_reader:
               if row['stop_code'] in stops:
                   if Kv1Stop.objects.filter(userstopcode=row['stop_code']).count() == 0:
                       s = Kv1Stop()
                       s.dataownercode = agency[stops.index(row['stop_code'])]
                       s.name = row['stop_name']
                       s.userstopcode = row['stop_code']
                       s.location = Point(float(row['stop_lon']), float(row['stop_lat']), srid=4326)
                       s.save()