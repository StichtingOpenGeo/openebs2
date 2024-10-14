from builtins import object
import logging
from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Hidden
import floppyforms.__future__ as forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from kv1.models import Kv1Journey, Kv1JourneyDate, Kv1Line, Kv1Stop
from kv15.enum import REASONTYPE, SUBREASONTYPE, ADVICETYPE, SUBADVICETYPE, MONITORINGERROR
from openebs.models import Kv17Change, Kv17Shorten
from openebs.models import Kv17JourneyChange, Kv17MutationMessage
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta, time
from django.db.models import Q
from django.utils.timezone import make_aware
from utils.time import hhmm_to_seconds


log = logging.getLogger('openebs.forms')


class Kv17ChangeForm(forms.ModelForm):
    # This is duplication, but should work
    operatingday = forms.ChoiceField(label=_("Datum"), required=True)
    begintime_part = forms.TimeField(label=_('Ingangstijd'), required=False, widget=forms.TimeInput(format='%H:%M:%S'))
    endtime_part = forms.TimeField(label=_('Eindtijd'), required=False, widget=forms.TimeInput(format='%H:%M:%S'))
    reasontype = forms.ChoiceField(choices=REASONTYPE, label=_("Type oorzaak"), required=False)
    subreasontype = forms.ChoiceField(choices=SUBREASONTYPE, label=_("Oorzaak"), required=False)
    reasoncontent = forms.CharField(max_length=255, label=_("Uitleg oorzaak"), required=False,
                                    widget=forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}))
    advicetype = forms.ChoiceField(choices=ADVICETYPE, label=_("Type advies"), required=False)
    subadvicetype = forms.ChoiceField(choices=SUBADVICETYPE, label=_("Advies"), required=False)
    advicecontent = forms.CharField(max_length=255, label=_("Uitleg advies"), required=False,
                                    widget=forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}))
    monitoring_error = forms.ChoiceField(choices=MONITORINGERROR, required=False)

    def clean(self):
        cleaned_data = super(Kv17ChangeForm, self).clean()
        operatingday = parse_date(self.data['operatingday'])
        if operatingday is None:
            raise ValidationError(_("Er staan geen ritten in de database"))

        if 'journeys' not in self.data:
            raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig"))

        if self.data['begintime_part'] != '':
            hh, mm = self.data['begintime_part'].split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))
        else:
            begintime = None

        if self.data['endtime_part'] != '':
            hh_e, mm_e = self.data['endtime_part'].split(':')
            endtime = make_aware(datetime.combine(operatingday, time(int(hh_e), int(mm_e))))
            if begintime:
                if begintime > endtime:  # if endtime before begintime
                    endtime = endtime + timedelta(days=1)  # endtime is next day
                    if endtime.time() >= time(6, 0):  # and after 6 am: validation error
                        raise ValidationError(_("Eindtijd valt op volgende operationele dag"))
        else:
            endtime = None

        dataownercode = self.user.userprofile.company
        if 'Alle ritten' in self.data['journeys']:
            valid_journeys, cleaned_data['recovered_changes'] = self.clean_all_journeys(operatingday, dataownercode, begintime, endtime)
        elif 'Hele vervoerder' in self.data['lines']:
            valid_journeys, cleaned_data['recovered_changes'] = self.clean_all_lines(operatingday, dataownercode, begintime, endtime)
        else:
            valid_journeys, cleaned_data['recovered_changes'] = self.clean_journeys(operatingday, dataownercode)

        if valid_journeys == 0:
            raise ValidationError(_("Er zijn geen ritten geselecteerd om op te heffen"))

        return cleaned_data

    def clean_journeys(self, operatingday, dataownercode):
        valid_journeys = 0
        recovered_changes = []
        if self.data['journeys'] != '':
            for journey in self.data['journeys'].split(',')[0:-1]:
                journey_qry = Kv1Journey.objects.filter(dataownercode=dataownercode, pk=journey, dates__date=operatingday)
                if journey_qry.count() == 0:
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig"))

                database = Kv17Change.objects.filter(journey__pk=journey,
                                                     line=journey_qry[0].line,
                                                     dataownercode=dataownercode,
                                                     operatingday=operatingday,
                                                     is_recovered=False)

                if 'Annuleren' in self.data:
                    if database.filter(is_cancel=True):
                        raise ValidationError(_("Een of meer geselecteerde ritten zijn al aangepast."))

                    # delete recovered if query is the same.
                    Kv17Change.objects.filter(dataownercode=dataownercode,
                                              journey__pk=journey,
                                              line=journey_qry[0].line,
                                              operatingday=operatingday,
                                              is_recovered=True,
                                              is_cancel=True).delete()

                    # change not_monitored to 'recovered=True' if cancel_query is the same
                    registered_changes = Kv17Change.objects.filter(journey__pk=journey,
                                                                   dataownercode=dataownercode,
                                                                   line=journey_qry[0].line,
                                                                   operatingday=operatingday,
                                                                   monitoring_error__isnull=False,
                                                                   is_recovered=False)
                    if registered_changes.count() != 0:
                        registered_change_ids = list(registered_changes.values_list('id', flat=True))
                        for reg in registered_changes:
                            reg.recover()
                        for recovered in Kv17Change.objects.filter(id__in=registered_change_ids):
                            recovered_changes.append(recovered)

                else:  # NotMonitored Journey
                    if database.filter(Q(monitoring_error__isnull=False) | Q(is_cancel=True)):
                        raise ValidationError(_("Een of meer geselecteerde ritten zijn al aangepast"))

                    # delete recovered if query is the same.
                    Kv17Change.objects.filter(journey__pk=journey,
                                              line=journey_qry[0].line,
                                              dataownercode=dataownercode,
                                              operatingday=operatingday,
                                              monitoring_error__isnull=False,
                                              is_recovered=True).delete()
        else:
            raise ValidationError(_("Er werd geen rit geselecteerd."))

        valid_journeys += 1

        return valid_journeys, recovered_changes

    def clean_all_journeys(self, operatingday, dataownercode, begintime, endtime):
        valid_journeys = 0
        recovered_changes = []
        if 'lines' in self.data:
            if self.data['lines'] != '':
                for line in self.data['lines'].split(',')[0:-1]:
                    line_qry = Kv1Line.objects.filter(pk=line)

                    if line_qry.count() == 0:
                        raise ValidationError(_("Geen lijn gevonden."))

                    database_alljourneys = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                                     is_alljourneysofline=True, line=line_qry[0],
                                                                     operatingday=operatingday, is_recovered=False)

                    database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                                  is_alllines=True, operatingday=operatingday,
                                                                  is_recovered=False)

                    if 'Annuleren' in self.data:

                        # delete recovered if query is the same.
                        Kv17Change.objects.filter(dataownercode=dataownercode,
                                                  line=line_qry[0],
                                                  is_alljourneysofline=True,
                                                  is_recovered=True,
                                                  is_cancel=True,
                                                  operatingday=operatingday,
                                                  begintime=begintime,
                                                  endtime=endtime).delete()

                        # change not_monitored to 'recovered=True' if cancel_query is the same
                        registered_changes = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                                       line=line_qry[0],
                                                                       is_alljourneysofline=True,
                                                                       is_recovered=False,
                                                                       monitoring_error__isnull=False,
                                                                       operatingday=operatingday,
                                                                       begintime=begintime,
                                                                       endtime=endtime)
                        if registered_changes.count() != 0:
                            registered_change_ids = list(registered_changes.values_list('id', flat=True))
                            for reg in registered_changes:
                                reg.recover()
                            for recovered in Kv17Change.objects.filter(id__in=registered_change_ids):
                                recovered_changes.append(recovered)

                        if operatingday == datetime.today().date():
                            begintime = make_aware(datetime.now()) if begintime is None else begintime
                        else:
                            begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                                if begintime is None else begintime

                        if database_alllines:
                            if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                        Q(begintime__lte=begintime) | Q(begintime=None),
                                                        is_cancel=True):
                                raise ValidationError(_(
                                    "De gehele vervoerder is al aangepast voor de aangegeven ingangstijd."))

                        elif database_alljourneys:
                            if database_alljourneys.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                           Q(begintime__lte=begintime) | Q(begintime=None),
                                                           is_cancel=True):
                                raise ValidationError(_(
                                    "Een of meer geselecteerde lijnen zijn al aangepast voor de aangegeven ingangstijd."))

                    else:  # NotMonitored Line
                        # delete recovered if query is the same.
                        Kv17Change.objects.filter(dataownercode=dataownercode,
                                                  line=line_qry[0],
                                                  is_alljourneysofline=True,
                                                  is_recovered=True,
                                                  monitoring_error__isnull=False,
                                                  operatingday=operatingday,
                                                  begintime=begintime,
                                                  endtime=endtime).delete()

                        if operatingday == datetime.today().date():
                            begintime = make_aware(datetime.now()) if begintime is None else begintime
                        else:
                            begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                                if begintime is None else begintime

                        if database_alllines:
                            if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                        Q(begintime__lte=begintime) | Q(begintime=None),
                                                        Q(is_cancel=True) | Q(monitoring_error__isnull=False)):
                                raise ValidationError(_(
                                    "De gehele vervoerder is al aangepast voor de aangegeven ingangstijd."))

                        elif database_alljourneys:
                            if database_alljourneys.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                           Q(begintime__lte=begintime) | Q(begintime=None),
                                                           Q(is_cancel=True) | Q(monitoring_error__isnull=False)):
                                raise ValidationError(_(
                                    "Een of meer geselecteerde lijnen zijn al aangepast voor de aangegeven ingangstijd."))

        else:
            raise ValidationError(_("Geen geldige lijn geselecteerd"))

        valid_journeys += 1

        return valid_journeys, recovered_changes

    def clean_all_lines(self, operatingday, dataownercode, begintime, endtime):
        valid_journeys = 0
        recovered_changes = []
        database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode, is_alllines=True,
                                                      operatingday=operatingday, is_recovered=False)

        if 'Annuleren' in self.data:
            # delete recovered if query is the same.
            Kv17Change.objects.filter(dataownercode=dataownercode,
                                      is_alllines=True,
                                      is_cancel=True,
                                      is_recovered=True,
                                      operatingday=operatingday,
                                      begintime=begintime,
                                      endtime=endtime).delete()

            # change not_monitored to 'recovered=True' if cancel_query is the same
            # can't be a shorten, because 'is_alllines'
            registered_changes = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                           is_alllines=True,
                                                           monitoring_error__isnull=False,
                                                           is_recovered=False,
                                                           operatingday=operatingday,
                                                           begintime=begintime,
                                                           endtime=endtime)
            if registered_changes.count() != 0:
                registered_change_ids = list(registered_changes.values_list('id', flat=True))
                for reg in registered_changes:
                    reg.recover()
                for recovered in Kv17Change.objects.filter(id__in=registered_change_ids):
                    recovered_changes.append(recovered)

            if database_alllines:
                if operatingday == datetime.today().date():
                    begintime = make_aware(datetime.now()) if begintime is None else begintime
                else:
                    begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                        if begintime is None else begintime

                if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                        Q(begintime__lte=begintime) | Q(begintime=None)):
                    raise ValidationError(_("De ingangstijd valt al binnen een geplande operatie."))

        else:  # NotMonitored dataownercode
            # delete recovered if query is the same.
            Kv17Change.objects.filter(dataownercode=dataownercode,
                                      is_alllines=True,
                                      monitoring_error__isnull=False,
                                      is_recovered=True,
                                      operatingday=operatingday,
                                      begintime=begintime,
                                      endtime=endtime).delete()

            if database_alllines:
                if operatingday == datetime.today().date():
                    begintime = make_aware(datetime.now()) if begintime is None else begintime
                else:
                    begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                        if begintime is None else begintime
                if database_alllines.filter(Q(monitoring_error__isnull=False) | Q(is_cancel=True),
                                            Q(endtime__gt=begintime) | Q(endtime=None),
                                            Q(begintime__lte=begintime) | Q(begintime=None)):
                    raise ValidationError(_(
                        "De gehele vervoerder is al aangepast voor de aangegeven ingangstijd."))

        valid_journeys += 1

        return valid_journeys, recovered_changes

    def save(self, force_insert=False, force_update=False, commit=True):
        ''' Save each of the journeys in the model. This is a disaster, we return the XML
        TODO: Figure out a better solution fo this! '''
        operatingday = parse_date(self.data['operatingday'])
        if self.data['begintime_part'] != '':
            hh, mm = self.data['begintime_part'].split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))
        else:
            begintime = None

        if self.data['endtime_part'] != '':
            hh_end, mm_end = self.data['endtime_part'].split(':')
            # if begintime is set and endtime is earlier than begintime add 1 day to operatingday of endtime
            if begintime and time(int(hh_end), int(mm_end)) < time(int(hh), int(mm)):
                if time(0, 0) <= time(int(hh_end), int(mm_end)) < time(6, 0):
                    operatingday_endtime = operatingday + timedelta(days=1)
                endtime = make_aware(datetime.combine(operatingday_endtime, time(int(hh_end), int(mm_end))))
            # else, operatingday is given day
            else:
                endtime = make_aware(datetime.combine(operatingday, time(int(hh_end), int(mm_end))))
        else:
            endtime = None

        if 'Annuleren' in self.data:
            if 'Alle ritten' in self.data['journeys']:
                to_send, to_recover = self.save_all_journeys(operatingday, begintime, endtime)
            elif 'Hele vervoerder' in self.data['lines']:
                to_send, to_recover = self.save_all_lines(operatingday, begintime, endtime)
            else:
                to_send, to_recover = self.save_journeys(operatingday)
        else:
            to_send, to_recover = self.save_not_monitored(operatingday, begintime, endtime)

        for recovered_change in self.instance.recovered_changes:
            to_recover.add(recovered_change.to_xml())

        xml_output = list(to_recover.union(to_send))
        return xml_output

    def save_all_journeys(self, operatingday, begintime, endtime):
        to_recover = set()
        to_send = set()

        """ only cancels in this function """
        for line in self.data['lines'].split(',')[0:-1]:
            qry = Kv1Line.objects.filter(id=line)
            if qry.count() == 0:
                log.error("Failed to find line %s" % line)
                continue
            new_recovered_changes = self.recover_changes('all_journeys', 'cancel', qry[0], operatingday, begintime,
                                                         endtime)
            for new_recovered_change in new_recovered_changes:
                to_recover.add(new_recovered_change.to_xml())

            self.instance.pk = None
            self.instance.is_alljourneysofline = True
            self.instance.line = qry[0]
            self.instance.operatingday = operatingday
            self.instance.begintime = begintime
            self.instance.endtime = endtime
            self.instance.is_cancel = True
            self.instance.monitoring_error = None
            self.instance.showcancelledtrip = True if self.data.get('showcancelledtrip', '') == 'on' else False
            self.instance.autorecover = True if self.data.get('autorecover', '') == 'on' else False

            # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
            if self.instance.line.dataownercode == self.instance.dataownercode:
                self.instance.save()

                # Add details
                if self.data['reasontype'] != '0' or self.data['advicetype'] != '0':
                    Kv17JourneyChange(change=self.instance, reasontype=self.data['reasontype'],
                                      subreasontype=self.data['subreasontype'],
                                      reasoncontent=self.data['reasoncontent'],
                                      advicetype=self.data['advicetype'],
                                      subadvicetype=self.data['subadvicetype'],
                                      advicecontent=self.data['advicecontent']).save()

                to_send.add(self.instance.to_xml())
            else:
                log.error(
                    "Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving all_journey cancel" %
                    (self.instance.line.dataownercode, self.instance.dataownercode))

        return to_send, to_recover

    def save_journeys(self, operatingday):
        to_recover = set()
        to_send = set()

        for journey in self.data['journeys'].split(',')[0:-1]:
            qry = Kv1Journey.objects.filter(id=journey, dates__date=operatingday)
            if qry.count() == 0:
                log.error("Failed to find journey %s" % journey)
                continue

            new_recovered_changes = self.recover_changes('journeys', 'cancel', qry[0], operatingday, None, None)
            for new_recovered_change in new_recovered_changes:
                to_recover.add(new_recovered_change.to_xml())

            qry_kv17change = Kv17Change.objects.filter(operatingday=operatingday, journey__id=journey,
                                                       is_recovered=False, is_cancel=False)
            if qry_kv17change.count() != 0:
                registered_other_ids = list(qry_kv17change.values_list('id', flat=True))
                for kv17change in qry_kv17change:
                    kv17change.recover()
                for new_recovered in set(Kv17Change.objects.filter(id__in=registered_other_ids)):
                    new_recovered_changes.append(new_recovered)
                for new_recovered_change in new_recovered_changes:
                    to_recover.add(new_recovered_change.to_xml())

            """ only cancels in this function """
            if qry.count() == 1:
                self.instance.pk = None
                self.instance.journey = qry[0]
                self.instance.line = qry[0].line
                self.instance.operatingday = operatingday
                self.instance.is_cancel = True
                self.instance.monitoring_error = None
                # Shouldn't be necessary, but just in case:
                self.instance.begintime = None
                self.instance.endtime = None
                self.instance.showcancelledtrip = True if self.data.get('showcancelledtrip', '') == 'on' else False
                self.instance.autorecover = True if self.data.get('autorecover', '') == 'on' else False

                # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
                if self.instance.journey.dataownercode == self.instance.dataownercode:
                    self.instance.save()

                    # Add details
                    if self.data['reasontype'] != '0' or self.data['advicetype'] != '0':
                        Kv17JourneyChange(change=self.instance, reasontype=self.data['reasontype'],
                                          subreasontype=self.data['subreasontype'],
                                          reasoncontent=self.data['reasoncontent'],
                                          advicetype=self.data['advicetype'],
                                          subadvicetype=self.data['subadvicetype'],
                                          advicecontent=self.data['advicecontent']).save()

                    to_send.add(self.instance.to_xml())
                else:
                    log.error(
                        "Oops! mismatch between dataownercode of journey (%s) and of user (%s) when saving journey cancel" %
                        (self.instance.journey.dataownercode, self.instance.dataownercode))

        return to_send, to_recover

    def save_all_lines(self, operatingday, begintime, endtime):
        to_recover = set()
        to_send = set()
        new_recovered_changes = self.recover_changes('all_lines', 'cancel', self.instance.dataownercode, operatingday,
                                                     begintime, endtime)
        for new_recovered_change in new_recovered_changes:
            to_recover.add(new_recovered_change.to_xml())

        self.instance.pk = None
        self.instance.is_alllines = True
        self.instance.operatingday = operatingday
        self.instance.begintime = begintime
        self.instance.endtime = endtime
        self.instance.is_cancel = True
        self.instance.monitoring_error = None
        self.instance.showcancelledtrip = True if self.data.get('showcancelledtrip', '') == 'on' else False
        self.instance.autorecover = True if self.data.get('autorecover', '') == 'on' else False

        # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
        if self.instance.dataownercode == self.user.userprofile.company:
            self.instance.save()

            # Add details
            if self.data['reasontype'] != '0' or self.data['advicetype'] != '0':
                Kv17JourneyChange(change=self.instance, reasontype=self.data['reasontype'],
                                  subreasontype=self.data['subreasontype'],
                                  reasoncontent=self.data['reasoncontent'],
                                  advicetype=self.data['advicetype'],
                                  subadvicetype=self.data['subadvicetype'],
                                  advicecontent=self.data['advicecontent']).save()

            to_send.add(self.instance.to_xml())
        else:
            log.error(
                "Oops! mismatch between dataownercode of request (%s) and of user (%s) when saving all_lines cancel" %
                (self.instance.dataownercode, self.user.userprofile.company))

        return to_send, to_recover

    def save_not_monitored(self, operatingday, begintime, endtime):
        to_recover = set()
        to_send = set()

        if 'Hele vervoerder' in self.data['lines']:  # hele vervoerder
            new_recovered_changes, keep_changes = self.recover_changes('all_lines', 'not_monitored',
                                                                       self.instance.dataownercode, operatingday,
                                                                       begintime, endtime)
            for keep in keep_changes:
                to_send.add(keep.to_xml())
            new_entries = []
            for new_recovered_change in new_recovered_changes:
                to_recover.add(new_recovered_change.to_xml())

                """ create copy of recovered changes to send with new xml """
                if new_recovered_change.shorten_details.all().count() > 0:
                    new_entry = new_recovered_change
                    new_entry.pk = None
                    new_entry.monitoring_error = None
                    new_entry.recovered = None
                    new_entry.is_recovered = False
                    new_entry.save()

                    """ make + add clone of all related shorten_details """
                    old_shorten_details = new_recovered_change.shorten_details.all()
                    for old_detail in old_shorten_details:
                        old_detail.pk = None
                        old_detail.save()
                        new_entry.shorten_details.add(old_detail)
                    new_entries.append(new_entry)

            for new_entry in new_entries:
                to_send.add(new_entry.to_xml())

            self.instance.pk = None
            self.instance.operatingday = operatingday
            self.instance.monitoring_error = self.data['notMonitored']
            self.instance.autorecover = False
            self.instance.showcancelledtrip = False
            self.instance.is_cancel = False
            self.instance.is_alllines = True
            self.instance.begintime = begintime
            self.instance.endtime = endtime

            # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
            if self.instance.dataownercode == self.user.userprofile.company:
                self.instance.save()

                to_send.add(self.instance.to_xml())
            else:
                log.error(
                    "Oops! mismatch between dataownercode of request (%s) and of user (%s) when saving all_lines not_monitored" %
                    (self.instance.dataownercode, self.user.userprofile.company))

        elif 'Alle ritten' in self.data['journeys']:  # hele lijn(en)
            for line in self.data['lines'].split(',')[0:-1]:
                qry = Kv1Line.objects.filter(id=line)
                if qry.count() == 0:
                    log.error("Failed to find line %s" % line)
                    continue

                new_entries = []
                new_recovered_changes, keep_changes = self.recover_changes('all_journeys', 'not_monitored', qry[0],
                                                                           operatingday, begintime, endtime)
                for keep in keep_changes:
                    to_send.add(keep.to_xml())

                for new_recovered_change in new_recovered_changes:
                    to_recover.add(new_recovered_change.to_xml())

                    """ create copy of recovered changes to send with new xml """
                    new_entry = new_recovered_change
                    old_shorten_details = new_recovered_change.shorten_details.all()
                    new_entry.pk = None
                    new_entry.monitoring_error = None
                    new_entry.is_recovered = False
                    new_entry.recovered = None
                    new_entry.save()

                    """ make + add clone of all related shorten_details """
                    for old_detail in old_shorten_details:
                        old_detail.pk = None
                        old_detail.save()
                        new_entry.shorten_details.add(old_detail)
                    new_entries.append(new_entry)

                for new_entry in new_entries:
                    to_send.add(new_entry.to_xml())

                self.instance.pk = None
                self.instance.line = qry[0]
                self.instance.operatingday = operatingday
                self.instance.begintime = begintime
                self.instance.endtime = endtime
                self.instance.is_alljourneysofline = True
                self.instance.monitoring_error = self.data['notMonitored']
                self.instance.autorecover = False
                self.instance.showcancelledtrip = False
                self.instance.is_cancel = False

                # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
                if self.instance.line.dataownercode == self.instance.dataownercode:
                    self.instance.save()

                    to_send.add(self.instance.to_xml())
                else:
                    log.error(
                        "Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving all_journey not_monitored" %
                        (self.instance.line.dataownercode, self.instance.dataownercode))
        else:  # enkele rit(ten)
            for journey in self.data['journeys'].split(',')[0:-1]:
                qry = Kv1Journey.objects.filter(id=journey, dates__date=operatingday)
                if qry.count() == 0:
                    log.error("Failed to find journey %s" % journey)
                    continue
                new_recovered_changes, keep_changes = self.recover_changes('journeys', 'not_monitored', qry[0],
                                                                           operatingday, begintime, endtime)

                new_details = []
                for new_recovered_change in new_recovered_changes:
                    to_recover.add(new_recovered_change.to_xml())
                    old_shorten_details = new_recovered_change.shorten_details.all()
                    """ make + add clone of all related shorten_details """
                    for old_detail in old_shorten_details:
                        old_detail.pk = None
                        old_detail.save()
                        new_details.append(old_detail)

                self.instance.pk = None
                self.instance.journey = qry[0]
                self.instance.line = qry[0].line
                self.instance.operatingday = operatingday
                self.instance.begintime = None
                self.instance.endtime = None
                self.instance.monitoring_error = self.data['notMonitored']
                self.instance.autorecover = False
                self.instance.showcancelledtrip = False
                self.instance.is_cancel = False

                # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
                if self.instance.journey.dataownercode == self.instance.dataownercode:
                    self.instance.save()

                    if len(new_recovered_changes) > 0 and len(new_details) > 0:
                        self.instance.shorten_details.set(new_details)

                    to_send.add(self.instance.to_xml())
                else:
                    log.error(
                        "Oops! mismatch between dataownercode of journey (%s) and of user (%s) when saving journey not_monitored" %
                        (self.instance.journey.dataownercode, self.instance.dataownercode))

        return to_send, to_recover

    def recover_changes(self, task, new_obj_type, current_object, operatingday, begintime, endtime):
        new_recovered_changes = []
        keep_changes = []
        if task == 'all_lines':
            if current_object != self.user.userprofile.company:
                return []
            qry_kv17change = Kv17Change.objects.filter(dataownercode=current_object, operatingday=operatingday,
                                                       is_recovered=False, is_cancel=False)

        elif task == 'all_journeys':
            if current_object.dataownercode != self.instance.dataownercode:
                return []
            qry_kv17change = Kv17Change.objects.filter(line=current_object, operatingday=operatingday,
                                                       is_recovered=False, is_cancel=False)

        elif task == 'journeys':
            if current_object.dataownercode != self.instance.dataownercode:
                return []
            qry_kv17change = Kv17Change.objects.filter(journey=current_object, operatingday=operatingday,
                                                       is_recovered=False, is_cancel=False)
        else: # should not be possible, but just in case
            return []

        if (task == 'all_lines' or task == 'all_journeys') and (begintime or endtime):
            if begintime:
                begintime_in_seconds = hhmm_to_seconds('begin', begintime)
                qry_kv17change = qry_kv17change.filter(Q(journey__departuretime__gte=begintime_in_seconds) |
                                                       Q(begintime__gte=begintime))
            if endtime:
                endtime_in_seconds = hhmm_to_seconds('end', endtime)

                qry_kv17change = qry_kv17change.filter(Q(journey__departuretime__lt=endtime_in_seconds) |
                                                       Q(endtime__lt=endtime))

        # keep shorten objects when new object is clustered not-monitored
        if (task == 'all_lines' or task == 'all_journeys') and new_obj_type == 'not_monitored':
            keep_changes = [x for x in qry_kv17change.filter(shorten_details__isnull=False).distinct('id')]
            qry_kv17change = qry_kv17change.filter(shorten_details__isnull=True)

        if qry_kv17change.count() != 0:
            registered_other_ids = list(qry_kv17change.values_list('id', flat=True))
            for kv17change in qry_kv17change:
                kv17change.recover()
            for new_recovered in set(Kv17Change.objects.filter(id__in=registered_other_ids)):
                new_recovered_changes.append(new_recovered)

        if new_obj_type == 'not_monitored':
            return new_recovered_changes, keep_changes
        else:
            return new_recovered_changes

    class Meta(object):
        model = Kv17Change
        exclude = ['dataownercode', 'line', 'journey', 'is_recovered', 'reinforcement']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Kv17ChangeForm, self).__init__(*args, **kwargs)

        days = [[str(d['date'].strftime('%Y-%m-%d')), str(d['date'].strftime('%d-%m-%Y'))] for d in
                Kv1JourneyDate.objects.all()
                              .filter(date__gte=datetime.today() - timedelta(days=1))
                              .values('date')
                              .distinct('date')
                              .order_by('date')]

        operating_day = days[((datetime.now().hour < 4) * -1) + 1] if len(days) > 1 else None
        self.fields['operatingday'].choices = days
        self.fields['operatingday'].initial = operating_day
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(_('Datum en tijd'),
                               'operatingday',
                               'begintime_part',
                               'endtime_part'
                               ),
                AccordionGroup(_('Oorzaak'),
                               'reasontype',
                               'subreasontype',
                               'reasoncontent'
                               ),
                AccordionGroup(_('Advies'),
                               'advicetype',
                               'subadvicetype',
                               'advicecontent'
                               ),
                AccordionGroup(_('Opties'),
                               'autorecover',
                               'showcancelledtrip'
                               )
            )
        )


class CancelLinesForm(forms.Form):
    verify_ok = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    def clean_verify_ok(self):
        if self.cleaned_data.get('verify_ok') is not True:
            raise ValidationError(_("Je moet goedkeuring geven om alle lijnen op te heffen"))

    def __init__(self, *args, **kwargs):
        super(CancelLinesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = 'journey_redbutton'
        self.helper.layout = Layout(
            Hidden('verify_ok', 'true'),
            Submit('submit', _("Hef alle ritten op"), css_class="text-center btn-danger btn-tall col-sm-3 pull-right")
        )


class Kv17ShortenForm(forms.ModelForm):
    operatingday = forms.ChoiceField(label=_("Datum"), required=True)
    begintime_part = forms.TimeField(label=_('Ingangstijd'), required=False, widget=forms.TimeInput(format='%H:%M:%S'))
    endtime_part = forms.TimeField(label=_('Eindtijd'), required=False, widget=forms.TimeInput(format='%H:%M:%S'))
    reasontype = forms.ChoiceField(choices=REASONTYPE, label=_("Type oorzaak"), required=False)
    subreasontype = forms.ChoiceField(choices=SUBREASONTYPE, label=_("Oorzaak"), required=False)
    reasoncontent = forms.CharField(max_length=255, label=_("Uitleg oorzaak"), required=False,
                                    widget=forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}))
    advicetype = forms.ChoiceField(choices=ADVICETYPE, label=_("Type advies"), required=False)
    subadvicetype = forms.ChoiceField(choices=SUBADVICETYPE, label=_("Advies"), required=False)
    advicecontent = forms.CharField(max_length=255, label=_("Uitleg advies"), required=False,
                                    widget=forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}))

    """ allJourneysOfLine mag niet in een verzamelbericht voor een SHORTEN. Iedere journey krijgt een eigen melding """

    # TODO: doe een poging vervallen haltes wel een icoontje te geven in ons scherm  --> nu alleen rit icoontje gegeven (geen blokkade)

    def clean(self):
        cleaned_data = super(Kv17ShortenForm, self).clean()
        cleaned_data['recovered_changes'] = []
        operating_day = self.data['operatingday']
        if operating_day is None:
            raise ValidationError(_("Er staan geen ritten in de database"))

        dataownercode = self.user.userprofile.company

        valid_journeys = 0
        if self.data['journeys'] != '':
            if 'Alle ritten' in self.data['journeys']:
                begintime = None
                endtime = None
                if 'begintime_part' in self.data.keys():
                    begintime = hhmm_to_seconds('begin', datetime.strptime(self.data['begintime_part'], "%H:%M"))
                if 'endtime_part' in self.data.keys():
                    endtime = hhmm_to_seconds('end', datetime.strptime(self.data['endtime_part'], "%H:%M"))

                all_journeys = Kv1Journey.objects.filter(dataownercode=dataownercode,
                                                         line=self.data['lines'],
                                                         dates__date=operating_day)
                if begintime and endtime:
                    cleaned_data['journeys'] = list(all_journeys.filter(departuretime__gte=begintime,
                                                                        departuretime__lte=endtime))
                elif begintime:
                    cleaned_data['journeys'] = list(all_journeys.filter(departuretime__gte=begintime))
                elif endtime:
                    cleaned_data['journeys'] = list(all_journeys.filter(departuretime__lte=endtime))
                else:
                    cleaned_data['journeys'] = list(all_journeys)
            else:
                journey_ids = [x for x in self.data['journeys'].split(',') if x]
                cleaned_data['journeys'] = list(Kv1Journey.objects.filter(dataownercode=dataownercode,
                                                                          pk__in=journey_ids,
                                                                          dates__date=operating_day))
                if len(cleaned_data['journeys']) < len(journey_ids):
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig"))
            cleaned_data['haltes'] = [x for x in self.data['haltes'].split(':')[1].split(',') if x]
            for journey in cleaned_data['journeys']:
                if journey.changes.all().filter(is_cancel=True, is_recovered=False).count() != 0:
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn al opgeheven"))

                registered_stopids = []
                registered_shortens = journey.changes.filter(shorten_details__isnull=False, operatingday=operating_day,
                                                             is_recovered=False)
                registered_others = journey.changes.filter(monitoring_error__isnull=False, shorten_details__isnull=True,
                                                           operatingday=operating_day, is_recovered=False)

                if registered_shortens.count() != 0:
                    registered_stopids = list(registered_shortens[0].shorten_details.all()
                                                                   .values_list('stop__pk', flat=True))

                valid_stops = []
                unique_stops = 0
                for line in self.data['haltes'].split(";"):
                    usc = []
                    if len(line) == 0:
                        continue
                    if line.split(":")[0] == journey.line.lineplanningnumber:
                        haltes = line.split(":")[1].split(",")
                        for halte in haltes:
                            if len(halte) == 0:
                                continue

                            halte_split = halte.split('_')
                            if len(halte_split) != 2:
                                continue
                            else:
                                usc.append(halte)

                            stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                            if stop:
                                valid_stops.append(stop.pk)
                            else:
                                raise ValidationError(
                                    _("Datafout: halte niet gevonden in database. Meld dit bij een beheerder."))

                            if Kv17Shorten.objects.filter(stop=stop.pk,
                                                          change__journey=journey,
                                                          change__operatingday=operating_day,
                                                          change__is_recovered=False).count() == 0:
                                unique_stops += 1
                    if set(valid_stops) == set(registered_stopids):
                        """ This SHORTEN was already registered for current journey; ignore for now, remove from current data """
                        cleaned_data['journeys'].remove(journey)
                        if len(cleaned_data['journeys']) == 0:
                            for userstopcode in usc:
                                cleaned_data['haltes'].remove(userstopcode)
                    elif valid_stops and registered_stopids:
                        registered_shorten_ids = set(registered_shortens.values_list('id', flat=True))
                        for reg in registered_shortens:
                            reg.recover()
                        for recovered in set(Kv17Change.objects.filter(id__in=registered_shorten_ids)):
                            cleaned_data['recovered_changes'].append(recovered)
                    elif registered_others:
                        registered_other_ids = set(registered_others.values_list('id', flat=True))
                        for reg in registered_others:
                            reg.recover()
                        for recovered in set(Kv17Change.objects.filter(id__in=registered_other_ids)):
                            cleaned_data['recovered_changes'].append(recovered)

                if len(valid_stops) == 0:
                    raise ValidationError(_("Selecteer minimaal een halte"))

                if unique_stops == 0 and cleaned_data['journeys']:
                    raise ValidationError(
                        _("De geselecteerde halte(s) zijn al aangepast voor de geselecteerde rit(ten)"))

                # if same shorten_query in database as 'is-recovered', delete
                old_recovered = Kv17Change.objects.filter(journey=journey, operatingday=operating_day,
                                                          is_cancel=False, is_recovered=True,
                                                          shorten_details__stop=stop).distinct('id')
                for old in old_recovered:
                    old.force_delete()

            valid_journeys += 1

        if valid_journeys == 0:
            raise ValidationError(_("Er zijn geen ritten geselecteerd om in te korten"))

        return cleaned_data


    def save(self, force_insert=False, force_update=False, commit=True):
        """ Save each of the journeys in the model. This is a disaster, we return the XML
        TODO: Figure out a better solution fo this! """
        operatingday = parse_date(self.data['operatingday'])
        to_recover = set()
        to_send = set()

        for recovered_change in self.instance.recovered_changes:
            to_recover.add(recovered_change.to_xml())

        new_recovered_changes = []
        for journey in self.cleaned_data['journeys']:
            qry_kv17change = Kv17Change.objects.filter(journey=journey, operatingday=operatingday, is_cancel=False,
                                                       is_recovered=False)
            if qry_kv17change.count() != 0:
                registered_other_ids = list(qry_kv17change.values_list('id', flat=True))
                for kv17change in qry_kv17change:
                    kv17change.recover()
                for new_recovered in set(Kv17Change.objects.filter(id__in=registered_other_ids)):
                    new_recovered_changes.append(new_recovered)
                for new_recovered_change in new_recovered_changes:
                    to_recover.add(new_recovered_change.to_xml())
                new_recovered_changes = []

            self.instance.pk = None
            self.instance.journey = journey
            self.instance.line = journey.line
            self.instance.operatingday = parse_date(self.data['operatingday'])
            self.instance.begintime = None
            self.instance.endtime = None
            self.instance.is_cancel = False
            self.instance.showcancelledtrip = True if self.data.get('showcancelledtrip', '') == 'on' else False
            self.instance.autorecover = True if self.data.get('autorecover', '') == 'on' else False
            self.instance.monitoring_error = None
            if len(self.instance.recovered_changes) > 0:
                self.instance.monitoring_error = self.instance.recovered_changes[0].monitoring_error
            elif len(new_recovered_changes) > 0:
                self.instance.monitoring_error = new_recovered_changes[0].monitoring_error

            # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
            if self.instance.dataownercode == self.user.userprofile.company:
                self.instance.save()
                self.save_shorten(qry_kv17change)
                self.save_mutationmessage()
                to_send.add(self.instance.to_xml())

            else:
                log.error(
                    "Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving journey cancel" %
                    (self.instance.journey.dataownercode, self.instance.dataownercode))

        xml_output = list(to_recover.union(to_send))
        return xml_output

    def save_shorten(self, qry_kv17change):
        for line in self.data['haltes'].split(";"):
            if line != '':
                lijn = self.instance.line
                if line.split(":")[0] == lijn.publiclinenumber:
                    haltes = line.split(":")[1].split(",")
                    for halte in haltes:
                        if len(halte) == 0:
                            continue

                        halte_split = halte.split('_')
                        if len(halte_split) != 2:
                            continue

                        stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])

                        if qry_kv17change.count() != 0:
                            ids = qry_kv17change.values_list('id', flat=True)[0]
                            if Kv17Shorten.objects.filter(change=self.instance,
                                                          change_id=ids, stop=stop,
                                                          # passagesequencenumber=0,   TODO: resolve this in the future
                                                          ).count() == 0:
                                Kv17Shorten(change=self.instance,
                                            change_id=ids, stop=stop,
                                            # passagesequencenumber=0,   TODO: resolve this in the future
                                            ).save()

                        else:
                            Kv17Shorten(change=self.instance, stop=stop,
                                        # passagesequencenumber=0,   TODO: resolve this in the future
                                        ).save()

    def save_mutationmessage(self):
        # Add details
        line = self.data['haltes']
        if line != '':
            lijn = self.instance.line
            if line.split(":")[0] == lijn.publiclinenumber:
                haltes = [x for x in line.split(":")[1].split(",") if x]
                for halte in haltes:
                    halte_split = halte.split('_')
                    if len(halte_split) != 2:
                        continue

                    stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])

                    if self.data['reasontype'] != '0' or self.data['advicetype'] != '0':
                        Kv17MutationMessage(change=self.instance,
                                            stop=stop,
                                            # passagesequencenumber=0,  # TODO: resolve this in the future
                                            reasontype=self.data['reasontype'],
                                            subreasontype=self.data['subreasontype'],
                                            reasoncontent=self.data['reasoncontent'],
                                            advicetype=self.data['advicetype'],
                                            subadvicetype=self.data['subadvicetype'],
                                            advicecontent=self.data['advicecontent']).save()

    class Meta(Kv17ChangeForm.Meta):
        model = Kv17Change
        exclude = ['dataownercode', 'line', 'journey', 'is_recovered', 'reinforcement', 'stop', 'monitoring_error',
                   'stops']

        # inherit 'showcancelledtrip' from kv17Change to avoid duplication
        fields = ('showcancelledtrip',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Kv17ShortenForm, self).__init__(*args, **kwargs)

        DAYS = [[str(d['date'].strftime('%Y-%m-%d')), str(d['date'].strftime('%d-%m-%Y'))] for d in
                Kv1JourneyDate.objects.all()
                                      .filter(date__gte=datetime.today() - timedelta(days=1))
                                      .values('date')
                                      .distinct('date')
                                      .order_by('date')]

        OPERATING_DAY = DAYS[((datetime.now().hour < 4) * -1) + 1] if len(DAYS) > 1 else None
        self.fields['operatingday'].choices = DAYS
        self.fields['operatingday'].initial = OPERATING_DAY
        self.fields['showcancelledtrip'].initial = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(_('Datum en Tijd'),
                               'operatingday',
                               'begintime_part',
                               'endtime_part'
                               ),
                AccordionGroup(_('Oorzaak'),
                               'reasontype',
                               'subreasontype',
                               'reasoncontent'
                               ),
                AccordionGroup(_('Advies'),
                               'advicetype',
                               'subadvicetype',
                               'advicecontent'
                               ),
                AccordionGroup(_('Opties'),
                               'showcancelledtrip'
                               )
            )
        )
