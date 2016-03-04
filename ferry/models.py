import os

from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now

from kv1.models import Kv1Line, Kv1Journey, Kv1Stop
from openebs.models import Kv17Change
from utils.time import get_operator_date


class FerryLine(models.Model):
    line = models.ForeignKey(Kv1Line, unique=True)
    stop_depart = models.ForeignKey(Kv1Stop, related_name="ferry_departure")
    stop_arrival = models.ForeignKey(Kv1Stop, related_name="ferry_arrival")

    class Meta:
        verbose_name = "Ferry"
        verbose_name_plural = "Ferries"

    def __str__(self):
        return "Veerboot %s" % (self.line)


class FerryKv6Messages(models.Model):
    ferry = models.ForeignKey(FerryLine)
    operatingday = models.DateField(default=now)
    journeynumber = models.PositiveIntegerField()  # 0 - 999999
    delay = models.IntegerField(default=0)  # Delay in seconds
    departed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ferry journey"
        verbose_name_plural = "Ferry journeys"
        unique_together = ('ferry', 'journeynumber', 'operatingday')

    def __str__(self):
        return "%s - Rit %s (Lijn %s)" % (self.operatingday, self.journeynumber, self.ferry)

    def to_kv6_init(self):
        return render_to_string('xml/kv6init.xml', {'object': self}).replace(os.linesep, '')

    def to_kv6_delay(self):
        return render_to_string('xml/kv6delay.xml', {'object': self}).replace(os.linesep, '')

    def to_kv17change(self):
        journey = Kv1Journey.find_from_journeynumber(self.line, self.journeynumber, self.operatingday)
        if journey:
            change, created = Kv17Change.objects.get_or_create(dataownercode=self.ferry.line.dataownercode,
                                                               operatingday=self.operatingday,
                                                               line=self.ferry.line, journey=journey)
            change.is_recovered = False  # Clear this
            change.recovered = None
            change.save()
            return change.to_xml()
        return None

    def to_kv17recover(self):
        self.cancelled = False
        self.save()
        journey = Kv1Journey.find_from_journeynumber(self.ferry.line, self.journeynumber, self.operatingday)
        if journey:
            changes = Kv17Change.objects.filter(dataownercode=self.ferry.line.dataownercode, operatingday=self.operatingday,
                                                line=self.ferry.line, journey=journey)
            if changes.count() > 0:
                change = changes[0]
                change.delete()
                return change.to_xml()
            else:
                return None

    @staticmethod
    def cancel_all(line_pk):
        date = get_operator_date()
        try:
            ferry = FerryLine.objects.get(pk=line_pk)
        except FerryLine.DoesNotExist:
            ferry = None
        if ferry:
            xml_out = []
            journeys = ferry.line.journeys.filter(dates__date=date)
            for j in journeys:
                m, created = FerryKv6Messages.objects.get_or_create(ferry=ferry, journeynumber=j.journeynumber,
                                                                    operatingday=date)
                if not m.departed:
                    m.cancelled = True
                    m.save()
                    xml_out.append(m.to_kv17change())
            return xml_out
        return []
