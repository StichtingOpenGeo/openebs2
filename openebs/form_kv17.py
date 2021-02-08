from builtins import object
import logging
from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Hidden
import floppyforms.__future__ as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1Journey, Kv1JourneyDate, Kv1Line
from kv15.enum import REASONTYPE, SUBREASONTYPE, ADVICETYPE, SUBADVICETYPE
from openebs.models import Kv17Change
from openebs.models import Kv17JourneyChange
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta, time
from django.db.models import Q
from django.utils.timezone import make_aware


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

    def clean(self):
        cleaned_data = super(Kv17ChangeForm, self).clean()
        operatingday = parse_date(self.data['operatingday'])
        validationerrors = []
        if operatingday is None:
            validationerrors.append(ValidationError(_("Er staan geen ritten in de database")))

        if 'journeys' not in self.data:
            validationerrors.append(ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig")))

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
                        validationerrors.append(ValidationError(_("Eindtijd valt op volgende operationele dag")))
        else:
            endtime = None

        dataownercode = self.user.userprofile.company
        if 'Alle ritten' in self.data['journeys']:
            validationerrors = self.clean_all_journeys(operatingday, dataownercode, begintime, endtime, validationerrors)
        elif 'Hele vervoerder' in self.data['lines']:
            validationerrors = self.clean_all_lines(operatingday, dataownercode, begintime, endtime, validationerrors)
        else:
            validationerrors = self.clean_journeys(operatingday, dataownercode, validationerrors)

        if len(validationerrors) != 0:
            raise ValidationError(validationerrors)
        else:
            return cleaned_data

    def clean_journeys(self, operatingday, dataownercode, validationerrors):
        if self.data['journeys'] != '':
            for journey in self.data['journeys'].split(',')[0:-1]:
                journey_qry = Kv1Journey.objects.filter(dataownercode=dataownercode, pk=journey,
                                                        dates__date=operatingday)
                if journey_qry.count() == 0:
                    validationerrors.append(ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig")))

                # delete recovered if query is the same.
                Kv17Change.objects.filter(dataownercode=dataownercode, journey__pk=journey, line=journey_qry[0].line,
                                          operatingday=operatingday, is_recovered=True).delete()

        else:
            validationerrors.append(ValidationError(_("Er werd geen rit geselecteerd.")))

        return validationerrors

    def clean_all_journeys(self, operatingday, dataownercode, begintime, endtime, validationerrors):
        if 'lines' in self.data:
            if self.data['lines'] != '':
                for line in self.data['lines'].split(',')[0:-1]:
                    line_qry = Kv1Line.objects.filter(pk=line)

                    if line_qry.count() == 0:
                        validationerrors.append(ValidationError(_("Er werd geen lijn gevonden in de database.")))

                    database_alljourneys = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                                     is_alljourneysofline=True, line=line_qry[0],
                                                                     operatingday=operatingday, is_recovered=False)

                    database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                                  is_alllines=True, operatingday=operatingday,
                                                                  is_recovered=False)

                    # delete recovered if query is the same.
                    Kv17Change.objects.filter(dataownercode=dataownercode, is_alljourneysofline=True, line=line_qry[0],
                                              operatingday=operatingday, begintime=begintime, endtime=endtime,
                                              is_recovered=True).delete()

                    if operatingday == datetime.today().date():
                        begintime = make_aware(datetime.now()) if begintime is None else begintime
                    else:
                        begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                            if begintime is None else begintime

                    if database_alllines:
                        if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                    Q(begintime__lte=begintime) | Q(begintime=None)):
                            validationerrors.append(ValidationError(_(
                                "De gehele vervoerder is al aangepast voor de aangegeven ingangstijd.")))

                    elif database_alljourneys:
                        if database_alljourneys.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                       Q(begintime__lte=begintime) | Q(begintime=None)):
                            validationerrors.append(ValidationError(_(
                                "Een of meer geselecteerde lijnen zijn al aangepast voor de aangegeven ingangstijd.")))
        else:
            validationerrors.append(ValidationError(_("Geen geldige lijn geselecteerd")))

        return validationerrors

    def clean_all_lines(self, operatingday, dataownercode, begintime, endtime, validationerrors):
        database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode, is_alllines=True,
                                                      operatingday=operatingday, is_recovered=False)

        # delete recovered if query is the same.
        Kv17Change.objects.filter(dataownercode=dataownercode, is_alllines=True, is_recovered=True,
                                  operatingday=operatingday, begintime=begintime, endtime=endtime).delete()

        if database_alllines:
            if operatingday == datetime.today().date():
                begintime = make_aware(datetime.now()) if begintime is None else begintime
            else:
                begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                    if begintime is None else begintime

            if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                        Q(begintime__lte=begintime) | Q(begintime=None)):
                validationerrors.append(ValidationError(_("De ingangstijd valt al binnen een geplande operatie.")))

        return validationerrors

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

        if 'Alle ritten' in self.data['journeys']:
            xml_output = self.save_all_journeys(operatingday, begintime, endtime)
        elif 'Hele vervoerder' in self.data['lines']:
            xml_output = self.save_all_lines(operatingday, begintime, endtime)
        else:
            xml_output = self.save_journeys(operatingday)

        return xml_output

    def save_all_journeys(self, operatingday, begintime, endtime):
        xml_output = []

        for line in self.data['lines'].split(',')[0:-1]:
            qry = Kv1Line.objects.filter(id=line)
            if qry.count() == 1:
                self.instance.pk = None
                self.instance.is_alljourneysofline = True
                self.instance.line = qry[0]
                self.instance.operatingday = operatingday
                self.instance.begintime = begintime
                self.instance.endtime = endtime
                self.instance.is_cancel = True

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

                    xml_output.append(self.instance.to_xml())
                else:
                    log.error(
                        "Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving journey cancel" %
                        (self.instance.line.dataownercode, self.instance.dataownercode))

            else:
                log.error("Failed to find line %s" % line)

        return xml_output

    def save_journeys(self, operatingday):
        xml_output = []

        for journey in self.data['journeys'].split(',')[0:-1]:
            qry = Kv1Journey.objects.filter(id=journey, dates__date=operatingday)
            if qry.count() == 1:
                self.instance.pk = None
                self.instance.journey = qry[0]
                self.instance.line = qry[0].line
                self.instance.operatingday = operatingday
                self.instance.is_cancel = True

                # Shouldn't be necessary, but just in case:
                self.instance.begintime = None
                self.instance.endtime = None

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

                    xml_output.append(self.instance.to_xml())
                else:
                    log.error(
                        "Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving journey cancel" %
                        (self.instance.journey.dataownercode, self.instance.dataownercode))
            else:
                log.error("Failed to find journey %s" % journey)

        return xml_output

    def save_all_lines(self, operatingday, begintime, endtime):
        xml_output = []

        self.instance.pk = None
        self.instance.is_alllines = True
        self.instance.operatingday = operatingday
        self.instance.begintime = begintime
        self.instance.endtime = endtime
        self.instance.is_cancel = True

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

            xml_output.append(self.instance.to_xml())
        else:
            log.error(
                "Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving journey cancel" %
                (self.instance.line.dataownercode, self.instance.dataownercode))

        return xml_output

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
