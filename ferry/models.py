from builtins import object
import os, datetime
from datetime import datetime as dt

from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from kv1.models import Kv1Line, Kv1Journey, Kv1Stop
from openebs.models import Kv17Change, Kv17StopChange, Kv15Scenario
from openebs2.settings import FERRY_FULL_REASONTYPE, FERRY_FULL_REASONCONTENT, FERRY_FULL_SUBREASONTYPE, CROSSOVER_HOUR
from utils.time import get_operator_date


class FerryLine(models.Model):
    line = models.OneToOneField(Kv1Line, verbose_name=_("Lijn"), on_delete=models.CASCADE)
    stop_depart = models.ForeignKey(Kv1Stop, verbose_name=_("Vertrekpunt"), related_name="ferry_departure", on_delete=models.CASCADE)
    stop_arrival = models.ForeignKey(Kv1Stop, verbose_name=_("Aankomstpunt"), related_name="ferry_arrival", on_delete=models.CASCADE)
    scenario_cancelled = models.ForeignKey(Kv15Scenario, verbose_name=_("Scenario 'Dienst uit vaart'"), blank=True, null=True, on_delete=models.CASCADE)
    enable_auto_messages = models.BooleanField(verbose_name=_("Verstuur automatisch KV6 berichten"), default=False)

    class Meta(object):
        verbose_name = "Veerboot"
        verbose_name_plural = "Veerboten"

    def __str__(self):
        return "Veerboot %s" % (self.line)

    def clean(self):
        super(FerryLine, self).clean()
        if self.scenario_cancelled is not None and self.scenario_cancelled.dataownercode != self.line.dataownercode:
            raise ValidationError({'scenario_cancelled': _('Scenario moet voor zelfde vervoerder als lijn zijn')})


class FerryKv6Messages(models.Model):
    class Status(object):
        INITIALIZED = 0
        READY = 1
        DEPARTED = 5
        ARRIVED = 10

    STATUS = (
        (Status.READY, _("Gereerd voor vertrek")),
        (Status.DEPARTED, _("Vertrokken")),
        (Status.ARRIVED, _("Aankomst")),
    )

    ferry = models.ForeignKey(FerryLine, verbose_name=_("Veerbootlijn"), on_delete=models.CASCADE)
    operatingday = models.DateField(default=now, verbose_name=_("Dienstregelingsdatum"))
    journeynumber = models.PositiveIntegerField(verbose_name=_("Ritnummer"),)  # 0 - 999999
    delay = models.IntegerField(blank=True, null=True, verbose_name=_("Vertraging"), help_text=_("In seconden"))  # Delay in seconds
    status = models.PositiveSmallIntegerField(default=Status.INITIALIZED, choices=STATUS, verbose_name=_("Status"))
    cancelled = models.BooleanField(default=False, verbose_name=_("Opgeheven?"))
    full = models.BooleanField(default=False, verbose_name=_("Is vol?"))

    created = models.DateTimeField(auto_now_add=True)
    status_updated = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = _("Afvaart")
        verbose_name_plural = _("Afvaarten")
        unique_together = ('ferry', 'journeynumber', 'operatingday')

    def __str__(self):
        return "%s - Rit %s (Lijn %s)" % (self.operatingday, self.journeynumber, self.ferry)

    def set_status(self, status):
        self.status = status
        self.status_updated = dt.now()
        self.save()

    def to_kv6_ready(self, direction=None):
        if direction is None:
            direction = self.get_direction()
        return render_to_string('xml/kv6ready.xml', {'object': self, 'direction': direction}).replace(os.linesep, '')

    def to_kv6_delay(self):
        return render_to_string('xml/kv6delay.xml', {'object': self}).replace(os.linesep, '')

    def to_kv6_departed(self, direction=None):
        if direction is None:
            direction = self.get_direction()
        return render_to_string('xml/kv6departed.xml', {'object': self, 'direction': direction}).replace(os.linesep, '')

    def to_kv6_arrived(self, direction=None):
        if direction is None:
            direction = self.get_direction()
        return render_to_string('xml/kv6arrived.xml', {'object': self, 'direction': direction}).replace(os.linesep, '')

    def to_kv17change(self):
        journey = Kv1Journey.find_from_journeynumber(self.ferry.line, self.journeynumber, self.operatingday)
        if journey:
            change, created = Kv17Change.objects.get_or_create(dataownercode=self.ferry.line.dataownercode,
                                                               operatingday=self.operatingday,
                                                               line=self.ferry.line, journey=journey)
            return journey, change
        return None, None

    def to_cancel(self):
        journey, change = self.to_kv17change()
        if change:
            change.is_cancel = True
            change.is_recovered = False  # Clear this
            change.recovered = None
            change.save()

            self.cancelled = True
            self.save()

            return change.to_xml()
        return None

    def to_full(self):
        journey, change = self.to_kv17change()
        if change:
            change.is_recovered = False
            change.is_cancel = False
            change.save()
            stop = self.ferry.stop_arrival if journey.direction == 1 else self.ferry.stop_depart
            stop_change = Kv17StopChange(change=change, type=5, stop=stop, stoporder=1,
                                         reasontype=FERRY_FULL_REASONTYPE, subreasontype=FERRY_FULL_SUBREASONTYPE,
                                         reasoncontent=FERRY_FULL_REASONCONTENT)
            stop_change.save()

            self.full = True
            self.save()

            return change.to_xml()
        return None

    def to_recover(self):
        # Recover cancels and/or full
        # TODO: Check KV6 flow and status
        self.cancelled = False
        self.full = False
        self.save()
        journey = Kv1Journey.find_from_journeynumber(self.ferry.line, self.journeynumber, self.operatingday)
        if journey:
            changes = Kv17Change.objects.filter(dataownercode=self.ferry.line.dataownercode,
                                                operatingday=self.operatingday,
                                                line=self.ferry.line, journey=journey)
            if changes.count() > 0:
                change = changes[0]
                change.delete()
                return change.to_xml()
            else:
                return None

    def get_direction(self):
        journey = Kv1Journey.find_from_journeynumber(self.ferry.line, self.journeynumber, self.operatingday)
        if journey:
            return journey.direction
        else:
            raise Kv1Journey.DoesNotExist()

    @staticmethod
    def send_cancel_scenario(ferry_pk, user):
        try:
            ferry = FerryLine.objects.get(pk=ferry_pk)
        except FerryLine.DoesNotExist:
            ferry = None
        if ferry and ferry.scenario_cancelled:
            tomorrow = (dt.now() + datetime.timedelta(days=1)).replace(hour=CROSSOVER_HOUR, minute=0, second=0)
            msgs = ferry.scenario_cancelled.plan_messages(user, dt.now(), tomorrow)
            return [m.to_xml() for m in msgs]
        return []

    @staticmethod
    def recover_cancel_scenario(ferry_pk):
        # TODO: figure out if implementing this has any use, currently done in the view
        pass

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
                if m.status < FerryKv6Messages.Status.DEPARTED and not m.cancelled:
                    msg = m.to_cancel()
                    if msg:
                        xml_out.append(msg)
            return xml_out
        return []
