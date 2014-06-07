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
        qry = """SELECT l.id, l.publiclinenumber, l.lineplanningnumber, lg.id as log_id, lg.vehiclenumber, lg.last_logged, lg.last_punctuality
        FROM kv1_kv1journey j
        JOIN kv1_kv1line l ON (j.line_id = l.id)
        JOIN kv1_kv1journeydate jd ON (jd.journey_id = j.id and jd.date = CURRENT_DATE)
        LEFT OUTER JOIN reports_kv6log lg ON (j.journeynumber = lg.journeynumber and jd.date = lg.operatingday and lg.lineplanningnumber = l.lineplanningnumber)
        WHERE j.dataownercode = 'HTM' AND ROUND(EXTRACT(EPOCH FROM CURRENT_TIME - INTERVAL '15 MIN')) BETWEEN j.departuretime and j.departuretime+j.duration
        ORDER BY l.lineplanningnumber;"""

        cursor = connection.cursor()
        cursor.execute(qry)
        journey_list = dictfetchall(cursor)
        output = { }
        for journey in journey_list:
            line = journey['lineplanningnumber']
            if line not in output:
                output[line] = { 'lineplanningnumber': line, 'publiclinenumber': journey['publiclinenumber'],
                                 'list': [], 'seen': 0, 'expected': 0 }
            output[line]['list'] += journey
            output[line]['expected'] += 1
            if journey['log_id'] is not None:
                output[line]['seen'] += 1
            output[line]['percentage'] = round((output[line]['seen'] / output[line]['expected']) * 100.0, 1)

        return output.values()


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]