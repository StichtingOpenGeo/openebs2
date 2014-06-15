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

        output = { key_func(datapoints[0]) : {'date': datapoints[0]['created'], 'seen' : 0, 'expected': 0, 'percentage': 0.0 }}
        last_key = None
        for point in datapoints:
            key = key_func(point)
            if last_key is not None and key != last_key:
                # Calculate percentage based on all the sightings
                if output[last_key]['expected'] == 0:
                    output[last_key]['percentage'] = 0.0
                else:
                    output[last_key]['percentage'] = round((float(output[last_key]['seen']) / float(output[last_key]['expected'])) * 100.0, 1)

                # Clear
                output[key] = {'date': point['created'], 'seen' : 0, 'expected': 0, 'percentage': 0.0 }

            for line in json.loads(point['data']):
                output[key]['seen'] += line['seen']
                output[key]['expected'] += line['expected']

            last_key = key

        return output.values()

    @staticmethod
    def do_graph_vehicles(date_range, key_func):
        datapoints = SnapshotLog.objects.filter(created__range=date_range).exclude(data='[]').order_by('created').values('created', 'data')
        output = { key_func(datapoints[0]) : {'date': datapoints[0]['created'], 'gtl' : 0, 'rr': 0, 'bus': 0 } }

        last_key = None
        for point in datapoints:
            key = key_func(point)
            if last_key is not None and key != last_key:
                output[key] = {'date': point['created'], 'gtl' : 0, 'rr': 0, 'bus': 0 }

            for line in json.loads(point['data']):
                for vehicle in line['list']:
                    if 'vehiclenumber' in vehicle and vehicle['vehiclenumber'] is not None:
                        if vehicle['vehiclenumber'][0] == '1':
                            output[key]['bus'] += 1
                        if vehicle['vehiclenumber'][0] == '3':
                            output[key]['gtl'] += 1
                        if vehicle['vehiclenumber'][0] == '4':
                            output[key]['rr'] += 1
            last_key = key
        return output

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