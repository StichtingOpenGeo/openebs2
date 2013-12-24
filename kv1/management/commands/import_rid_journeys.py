import csv
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.utils.timezone import now
from kv1.models import Kv1Journey, Kv1JourneyDate, Kv1Line


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.folder = args[0]
        print "==========================\r\nSTEP A: Journeys"
        self.do_journeys()
        #print "==========================\r\nSTEP B: Journey dates"
        #self.do_journey_dates()

    def do_journeys(self):
        self.log("Printing '.' for every 1000 saved trips")
        with open(self.folder+'/openebs_journeys.csv') as stops_file:
            journeystop_reader = csv.DictReader(stops_file, delimiter=',', quotechar='"')

            line = None
            create_buffer = []
            buffer_keys = []
            skip = 0
            for row in journeystop_reader:
                journey_code = row['journey_id'].split(':')
                if line is None or line.lineplanningnumber != journey_code[1]:
                    try:
                        line = Kv1Line.objects.get(dataownercode=journey_code[0], lineplanningnumber=journey_code[1])
                    except ObjectDoesNotExist:
                        line = None
                        self.log("Couldn't find line for journey: %s" % row['journey_id'])

                # Journey
                if line is not None:
                    q_journey = Kv1Journey.objects.filter(dataownercode=journey_code[0], line__lineplanningnumber=journey_code[1],
                                                        journeynumber=journey_code[2])
                    if q_journey.count() == 0 and row['journey_id'] not in buffer_keys:
                        # Create the journey
                        journey = Kv1Journey(dataownercode=journey_code[0], line=line, journeynumber=journey_code[2], direction=row['direction'])
                        journey.departuretime = float(row['base_departure_time'])
                        create_buffer.append(journey)
                        buffer_keys.append(row['journey_id'])
                    elif q_journey.count() > 0:
                        # Update existing trip
                        journey = q_journey[0]
                        journey.departuretime = float(row['base_departure_time'])
                        journey.save()
                    else:
                        skip += 1

                if len(create_buffer) > 0 and (len(create_buffer) % 1000) == 0:
                    print('.'),
                    Kv1Journey.objects.bulk_create(create_buffer)
                    create_buffer = []
                    buffer_keys = []

    def do_journey_dates(self):
        '''
        Disable this for now - too slow
        '''
        hit = 0
        miss = 0
        with open(self.folder+'/openebs_journey_dates.csv') as stops_file:
            journeydate_reader = csv.DictReader(stops_file, delimiter=',', quotechar='"')

            journey = None
            obj_buffer = []
            buffer_keys = []
            for row in journeydate_reader:
                # Start by checking if we really need to lookup this journey
                # Sorted datasets will now go much faster
                journey_code = row['privatecode'].split(':')
                if journey is None or (journey_code[0] != journey.dataownercode
                         or journey_code[1] != journey.line.lineplanningnumber
                         or journey_code[2] != journey.journeynumber):
                    q_journey = Kv1Journey.objects.filter(dataownercode=journey_code[0], line__lineplanningnumber=journey_code[1],
                                                            journeynumber=journey_code[2])
                    if q_journey.count() == 1:
                        journey = q_journey[0]
                    miss += 1
                else:
                    hit += 1

                if journey is not None:
                    # We have a journey, check if it hasn't already been added
                    if (journey, row['validdate']) not in buffer_keys \
                        and Kv1JourneyDate.objects.filter(journey=journey,
                                                          date=row['validdate']).count() == 0:
                        obj_buffer.append(Kv1JourneyDate(journey=journey, date=row['validdate']))
                        buffer_keys.append((journey, row['validdate']))
                else:
                    self.log("Failed to find journey %s" % row['privatecode'])

                if len(obj_buffer) % 1000 == 0:
                    self.log("Saving 1000 journey dates")
                    Kv1JourneyDate.objects.bulk_create(obj_buffer)
                    buffer_keys = []
                    obj_buffer = []
            self.log("Had %s hits and %s misses" % (hit, miss))

    def log(self, text):
        print "\r\n%s - import_rid_trips: %s" % (now().isoformat(), text)