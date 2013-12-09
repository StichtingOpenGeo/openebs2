import re, json
from os import listdir
from os.path import isfile, join, splitext, split
from django.core.management import BaseCommand
from kv1.models import Kv1Line, Kv1Stop


class Command(BaseCommand):

    help = 'Check all the stops we have in the stop maps/lists are actually in the database'

    def handle(self, *args, **options):
        missing_stops = []
        for line in Kv1Line.objects.exclude(stop_map='{}'):
            line_stops = []
            for line in line.stop_map:
                if 'left' in line and line['left'] is not None and line['left']['id'].split('_') not in line_stops:
                    line_stops.append(line['left']['id'].split('_'))
                if 'right' in line and line['right'] is not None and line['right']['id'].split('_') not in line_stops:
                    line_stops.append(line['right']['id'].split('_'))

                for stop in line_stops:
                    if stop not in missing_stops:
                        if Kv1Stop.objects.filter(dataownercode=stop[0], userstopcode=stop[1]).count() == 0:
                            missing_stops.append(stop)
                            print "Found missing stop %s %s " % (stop[0], stop[1])