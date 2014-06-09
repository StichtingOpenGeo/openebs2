from datetime import datetime
from django.db import models, connection
from kv1.models import Kv1Line
from kv15.enum import DATAOWNERCODE


class Kv6Log(models.Model):
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    lineplanningnumber = models.CharField(max_length=10)
    journeynumber = models.PositiveIntegerField(max_length=6)  # 0 - 999999
    operatingday = models.DateField()

    vehiclenumber = models.CharField(max_length=10, blank=True)

    last_punctuality = models.IntegerField()
    max_punctuality = models.IntegerField()
    last_logged = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('dataownercode', 'lineplanningnumber', 'journeynumber', 'operatingday')

    @staticmethod
    def do_report():
        now = datetime.now()
        qry = """SELECT j.line_id, j.journeynumber, lg.id as log_id, lg.vehiclenumber, lg.last_logged, lg.last_punctuality
        FROM kv1_kv1journey j
        JOIN kv1_kv1journeydate jd ON (jd.journey_id = j.id and jd.date = CURRENT_DATE)
        LEFT OUTER JOIN reports_kv6log lg ON (j.journeynumber = lg.journeynumber and jd.date = lg.operatingday)
        WHERE j.dataownercode = 'HTM' AND %s BETWEEN j.departuretime and j.arrivaltime
        ORDER BY j.line_id;""" % ((now.hour*60*60)+(now.minute*60)+now.second)

        cursor = connection.cursor()
        cursor.execute(qry)
        journey_list = dictfetchall(cursor)
        output = { }
        for journey in journey_list:
            line = journey['line_id']
            if line not in output:
                output[line] = { 'line_id': line, 'publiclinenumber': journey['line_id'],
                                 'list': [], 'live': [], 'seen': 0, 'expected': 0 }
            output[line]['list'].append(journey)
            output[line]['expected'] += 1
            if journey['log_id'] is not None:
                output[line]['seen'] += 1
                output[line]['live'].append(journey)
            output[line]['percentage'] = round((float(output[line]['seen']) / float(output[line]['expected'])) * 100, 1)

        list = sorted(output.values(), key= lambda k: k['percentage'])
        return sorted(list, key= lambda k: int(k['line_id']))


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]