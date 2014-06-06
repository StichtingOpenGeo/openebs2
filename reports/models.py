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
        qry = """select l.id, l.publiclinenumber, l.lineplanningnumber, coalesce(count(lg.id), 0) as seen, count(*) as planned, ROUND(100.0 * count(lg.id)/count(*),1) as percentage
        from kv1_kv1journey j
        join kv1_kv1line l on (j.line_id = l.id)
        join kv1_kv1journeydate jd on (jd.journey_id = j.id and jd.date = CURRENT_DATE)
        left outer join reports_kv6log lg on (j.journeynumber = lg.journeynumber and jd.date = lg.operatingday and lg.lineplanningnumber = l.lineplanningnumber)
        WHERE j.dataownercode = 'HTM' and
        j.departuretime between ROUND(EXTRACT(EPOCH FROM CURRENT_TIME - INTERVAL '30 MIN')) and ROUND(EXTRACT(EPOCH FROM CURRENT_TIME))
        group by l.id, l.lineplanningnumber
        order by percentage, l.lineplanningnumber::int;"""

        cursor = connection.cursor()
        cursor.execute(qry)
        return dictfetchall(cursor)

    @staticmethod
    def do_details():
        qry = """SELECT l.id, l.dataownercode, l.lineplanningnumber, j.journeynumber, j.departuretime, lg.id, lg.max_punctuality, lg.vehiclenumber
        FROM kv1_kv1journey j
        JOIN kv1_kv1line l ON (j.line_id = l.id)
        JOIN kv1_kv1journeydate jd ON (jd.journey_id = j.id and jd.date = CURRENT_DATE)
        LEFT OUTER JOIN reports_kv6log lg ON (j.journeynumber = lg.journeynumber and jd.date = lg.operatingday and lg.lineplanningnumber = l.lineplanningnumber)
        WHERE j.dataownercode = 'HTM' and
        j.departuretime < ROUND(EXTRACT(EPOCH FROM CURRENT_TIME))
        ORDER BY l.lineplanningnumber::int, j.departuretime;"""



def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]