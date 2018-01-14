from django.db import IntegrityError
from kv1.models import Kv1Journey
from openebs.models import Kv17Change
from django.utils.timezone import now
from openebs.views_push import Kv17PushMixin

pusher = Kv17PushMixin()
with open('staak.csv', 'r') as f:
    for y in f:
        print("Looking for "+y.strip("\n"))
        private, validdate = y[:-1].split(',')
        if private == 'privatecode':
            continue
        dataowner, lineplanningnumber, journeynumber = private.split(':')
        trips = Kv1Journey.find_from_realtime(dataowner, private)
        if trips is None:
            print "Not found:" + y.strip("\n")
        else:
            try:
                modification = Kv17Change(dataownercode=trips.dataownercode, operatingday=now(), line=trips.line, journey=trips)
                modification.save()
                pusher.push_message(modification.to_xml())
                print("Cancelled %s:%s:%s" % (trips.dataownercode, trips.line.lineplanningnumber, trips.journeynumber))
            except IntegrityError:
                print "Already exists: "+y.strip("\n")