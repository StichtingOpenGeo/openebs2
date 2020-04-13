from __future__ import division
from past.utils import old_div
from builtins import object
import logging
from datetime import time

from django.contrib.gis.db import models
from jsonfield import JSONField
from kv15.enum import DATAOWNERCODE, STOPTYPES
from django.utils.translation import ugettext_lazy as _

from utils.time import get_operator_date

log = logging.getLogger('openebs.models.kv1')


class Kv1Line(models.Model):
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    lineplanningnumber = models.CharField(max_length=10)
    publiclinenumber = models.CharField(max_length=10)
    headsign = models.CharField(max_length=100)
    stop_map = JSONField()

    class Meta(object):
        verbose_name = _("Lijn")
        verbose_name_plural = _("Lijninformatie")
        unique_together = ('dataownercode', 'lineplanningnumber')

    def __unicode__(self):
        return "%s - %s" % (self.dataownercode, self.headsign)


class Kv1Stop(models.Model):
    userstopcode = models.CharField(max_length=10)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    timingpointcode = models.CharField(max_length=10)  # Note, unique, but not per stop
    name = models.CharField(max_length=50)
    location = models.PointField()

    class Meta(object):
        verbose_name = _("Halte")
        verbose_name_plural = _("Halteinformatie")
        unique_together = ('dataownercode', 'userstopcode')

    def __unicode__(self):
        if self.timingpointcode and self.timingpointcode != "0":
            return "%s - %s (TPC %s, #%s)" % (self.dataownercode, self.name, self.timingpointcode, self.userstopcode)
        else:
            return "%s - %s (#%s)" % (self.dataownercode, self.name, self.userstopcode)

    @staticmethod
    def find_stop(dataowner, stopcode):
        result = Kv1Stop.objects.filter(dataownercode=dataowner, userstopcode=stopcode)
        if result.count() == 1:
            return result[0]

    @staticmethod
    def find_stops_from_haltes(halte_string):
        out = []
        for halte in halte_string.split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    out.append(stop)
        return out


class Kv1Journey(models.Model):
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    line = models.ForeignKey(Kv1Line, related_name="journeys",
                             on_delete=models.CASCADE)  # Represent lineplanningnumber\
    journeynumber = models.PositiveIntegerField()  # 0 - 999999
    scheduleref = models.PositiveIntegerField()  # Field 'availabilityconditionref'
    departuretime = models.PositiveIntegerField()
    direction = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return "%s%s - %s" % (self.dataownercode, self.line.publiclinenumber, self.journeynumber)

    @staticmethod
    def find_from_realtime(dataowner, realtime_id, date=get_operator_date()):
        j = realtime_id.split(':')
        log.info("Looking for realtime trip id %s on date %s" % (j, date))
        if len(j) == 3:
            line = Kv1Line.objects.filter(dataownercode=dataowner,
                                          lineplanningnumber=j[1])
            if line.count() == 1:
                journey_pk = Kv1Journey.objects.filter(dataownercode=dataowner,
                                                       line=line[0].pk,
                                                       journeynumber=int(j[2]),
                                                       dates__date=date)
                if journey_pk.count() == 1:
                    log.info("Found journey with id '%s' for realtime_id %s" % (journey_pk[0].id, realtime_id))
                    return journey_pk[0]
                else:
                    log.warn(
                        "Realtime trip id '%s' has an journey count of %s (not exactly 1)" % (realtime_id, journey_pk))
            else:
                log.warn("Realtime trip id '%s' has an invalid line" % (realtime_id,))
        else:
            log.warn("Realtime trip id '%s' has incorrect # of arguments" % (realtime_id,))
        log.error("Couldn't find trip  %s on date %s :(" % (j, date))
        return None

    @staticmethod
    def find_from_journeynumber(line, journeynumber, date):
        journeys = Kv1Journey.objects.filter(dataownercode=line.dataownercode,
                                             line=line.pk,
                                             journeynumber=journeynumber,
                                             dates__date=date)
        return journeys[0] if journeys.count() == 1 else None

    def departuretime_as_time(self):
        total_minutes = old_div(self.departuretime, 60)
        return time(hour=old_div(total_minutes, 60), minute=total_minutes % 60)

    class Meta(object):
        verbose_name = _("Rit")
        verbose_name_plural = _("Ritinformatie")
        unique_together = ('dataownercode', 'line', 'journeynumber', 'scheduleref')


class Kv1JourneyStop(models.Model):
    journey = models.ForeignKey(Kv1Journey, related_name="stops", on_delete=models.CASCADE)
    stop = models.ForeignKey(Kv1Stop, on_delete=models.CASCADE)
    stoporder = models.SmallIntegerField()
    stoptype = models.CharField(choices=STOPTYPES, default="INTERMEDIATE", max_length=12)
    targetarrival = models.TimeField()
    targetdeparture = models.TimeField()

    def __unicode__(self):
        return "%s - Stop #%s: %s" % (self.journey.journeynumber, self.stoporder, self.stop)

    class Meta(object):
        verbose_name = _("Rithalte")
        verbose_name_plural = _("Rithaltes")
        unique_together = (('journey', 'stop'), ('journey', 'stoporder'))


class Kv1JourneyDate(models.Model):
    journey = models.ForeignKey(Kv1Journey, related_name='dates', on_delete=models.CASCADE)  # A journey has dates
    date = models.DateField()

    def __unicode__(self):
        return "%s (%s)" % (self.journey.journeynumber, self.date)

    class Meta(object):
        verbose_name = _("Ritdag")
        verbose_name_plural = _("Ritdag")
        unique_together = (('journey', 'date'))
