from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date

pusher = Kv17PushMixin()
with open('nietstaak.csv', 'r') as f:
    for y in f:
        private, validdate = y[:-1].split(',')
        if private == 'privatecode':
            continue
        dataowner, lineplanningnumber, journeynumber = private.split(':')
        cancelled = Kv17Change.objects.filter(dataownercode=dataowner, line__lineplanningnumber=lineplanningnumber, journey__journeynumber=journeynumber, journey__dates__date=get_operator_date())
        if cancelled.count() == 1:
            cancelled[0].delete()
            pusher.push_message(cancelled[0].to_xml())
            print ("Oops, shouldn't have cancelled "+y.strip("\n"))
        if cancelled.count() > 1:
            print "Whut?"
