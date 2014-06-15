from datetime import datetime, timedelta, date, time
import json
from django.contrib.gis.db import models
from django.db import connection
from json_field import JSONField
from kv15.enum import DATAOWNERCODE
from django.utils.translation import ugettext_lazy as _


class Kv6Log(models.Model):
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    lineplanningnumber = models.CharField(max_length=10)
    journeynumber = models.PositiveIntegerField(max_length=6)  # 0 - 999999
    operatingday = models.DateField()

    vehiclenumber = models.CharField(max_length=10, blank=True)

    last_position = models.PointField(blank=True, null=True)
    last_punctuality = models.IntegerField()
    max_punctuality = models.IntegerField()
    last_logged = models.DateTimeField(auto_now=True)

    objects = models.GeoManager()

    class Meta:
        unique_together = ('dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday')

    @staticmethod
    def do_report():
        now = datetime.now()
        fifteen = datetime.now() - timedelta(minutes=15)
        qry = """SELECT l.lineplanningnumber, j.journeynumber, lg.id as log_id, lg.vehiclenumber, lg.last_logged, lg.last_punctuality
        FROM kv1_kv1journey j
        JOIN kv1_kv1line l on (j.line_id = l.id)
        JOIN kv1_kv1journeydate jd ON (jd.journey_id = j.id and jd.date = CURRENT_DATE)
        LEFT OUTER JOIN reports_kv6log lg ON (j.journeynumber = lg.journeynumber and jd.date = lg.operatingday)
        WHERE j.dataownercode = 'HTM' AND j.departuretime < %s and j.arrivaltime > %s
        ORDER BY j.line_id;""" % (((now.hour*60*60)+(now.minute*60)+now.second),
                                  ((fifteen.hour*60*60)+(fifteen.minute*60)+fifteen.second))

        cursor = connection.cursor()
        cursor.execute(qry)
        journey_list = dictfetchall(cursor)
        output = { }
        for journey in journey_list:
            line = journey['lineplanningnumber']
            if line not in output:
                output[line] = { 'lineplanningnumber': line, 'publiclinenumber': journey['lineplanningnumber'],
                                 'list': [], 'seen': 0, 'expected': 0 }
            output[line]['list'].append(journey)
            output[line]['expected'] += 1
            if journey['log_id'] is not None:
                output[line]['seen'] += 1
            output[line]['percentage'] = round((float(output[line]['seen']) / float(output[line]['expected'])) * 100, 1)

        list = sorted(output.values(), key= lambda k: k['percentage'])
        return sorted(list, key= lambda k: int(k['lineplanningnumber']))


class SnapshotLog(models.Model):
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    created = models.DateTimeField(auto_now=True)
    data = JSONField()

    class Meta:
        unique_together = ('dataownercode', 'created')
        permissions = (
            ("view_dashboard", _("Ritten dashboard bekijken")),
        )

    @staticmethod
    def do_snapshot():
        snapshot = SnapshotLog()
        snapshot.dataownercode = 'HTM'
        snapshot.data = json.dumps(Kv6Log.do_report(), default=dthandler)
        snapshot.save()

    @staticmethod
    def do_graph_journeys(date_range, key_func):
        ''' Parameters: a range of dates for which to search for and an anonymous function providing the key '''
        datapoints = SnapshotLog.objects.filter(created__range=date_range).exclude(data='[]').order_by('created').values('created', 'data')

        output = {}
        last_key = None
        for point in datapoints:
            key = key_func(point)
            if key != last_key:
                # Clear
                output[key] = {'date': point['created'], 'seen' : 0, 'expected': 0, 'percentage': 0.0 }

            for line in json.loads(point['data']):
                output[key]['seen'] += line['seen']
                output[key]['expected'] += line['expected']

            # Calculate percentage based on all the sightings - could be more efficient, works for now
            if output[key]['expected'] == 0:
                output[key]['percentage'] = 0.0
            else:
                output[key]['percentage'] = round((float(output[key]['seen']) / float(output[key]['expected'])) * 100.0, 1)

            last_key = key

        return output.values()

    @staticmethod
    def get_type(vehicle):
        if vehicle[0] == '1':
            type = 'bus'
        if vehicle[0] == '3':
            type = 'gtl'
        if vehicle[0] == '4':
            type = 'rr'
        return type

    @staticmethod
    def do_graph_vehicles(date_range, key_func):
        datapoints = SnapshotLog.objects.filter(created__range=date_range).exclude(data='[]').order_by('created').values('created', 'data')
        output = { key_func(datapoints[0]) : {'date': datapoints[0]['created'], 'gtl' : [], 'rr': [], 'bus': [] } }

        last_key = None
        for point in datapoints:
            key = key_func(point)
            if last_key is not None and key != last_key:
                output[key] = {'date': point['created'], 'gtl' : [], 'rr': [], 'bus': [] }

            for line in json.loads(point['data']):
                for vehicle in line['list']:
                    if 'vehiclenumber' in vehicle and vehicle['vehiclenumber'] is not None:
                        type = SnapshotLog.get_type(vehicle['vehiclenumber'])
                        if vehicle['vehiclenumber'] not in output[key][type]:
                            output[key][type].append(vehicle['vehiclenumber'])

            last_key = key

        # The above loop gathers unique vehicles, we need sums
        for key, val in output.items():
            val['bus'] = len(val['bus'])
            val['gtl'] = len(val['gtl'])
            val['rr'] = len(val['rr'])

        return output.values()

dthandler = lambda obj: (
     obj.isoformat()
     if isinstance(obj, datetime)
     or isinstance(obj, date)
     else None)

def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]