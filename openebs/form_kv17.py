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
from utils.time import get_operator_date
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import datetime, time, timedelta


log = logging.getLogger('openebs.forms')


class Kv17ChangeForm(forms.ModelForm):
    # This is duplication, but should work
    operatingday = forms.ChoiceField(label=_("Datum"), required=True)
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
        if operatingday is None:
            raise ValidationError(_("Er staan geen ritten in de database"))

        if 'journeys' not in self.data:
            raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig"))

        dataownercode = self.user.userprofile.company

        if 'Alle ritten' in self.data['journeys']:
            valid_journeys = self.clean_all_journeys(operatingday, dataownercode)
        elif 'Hele vervoerder' in self.data['lines']:
            valid_journeys = self.clean_all_lines(operatingday, dataownercode)
        else:
            valid_journeys = self.clean_journeys(operatingday, dataownercode)

        if valid_journeys == 0:
            raise ValidationError(_("Er zijn geen ritten geselecteerd om op te heffen"))

        return cleaned_data

    def clean_journeys(self, operatingday, dataownercode):
        valid_journeys = 0
        if self.data['journeys'] != '':
            for journey in self.data['journeys'].split(',')[0:-1]:
                journey_qry = Kv1Journey.objects.filter(dataownercode=dataownercode,
                                                        pk=journey,
                                                        dates__date=operatingday)
                if journey_qry.count() == 0:
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig"))

                if Kv17Change.objects.filter(dataownercode=dataownercode,
                                             journey__pk=journey,
                                             line=journey_qry[0].line,
                                             operatingday=operatingday,
                                             is_recovered=False).count() != 0:
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn al aangepast"))

                # delete recovered if query is the same.
                Kv17Change.objects.filter(dataownercode=dataownercode,
                                          journey__pk=journey,
                                          line=journey_qry[0].line,
                                          operatingday=operatingday,
                                          is_recovered=True).delete()

        else:
            raise ValidationError(_("Er werd geen rit geselecteerd."))

        valid_journeys += 1

        return valid_journeys

    def clean_all_journeys(self, operatingday, dataownercode):
        valid_journeys = 0

        if 'lines' in self.data:
            if self.data['lines'] != '':
                for line in self.data['lines'].split(',')[0:-1]:
                    line_qry = Kv1Line.objects.filter(pk=line)

                    if line_qry.count() == 0:
                        raise ValidationError(_("Geen lijn gevonden."))

                    if Kv17Change.objects.filter(dataownercode=dataownercode,
                                                 operatingday=operatingday,
                                                 line=line_qry[0],
                                                 is_alljourneysofline=True,
                                                 is_recovered=False).count() != 0:
                        raise ValidationError(_("De gehele lijn is al aangepast"))

                    # delete recovered if query is the same.
                    Kv17Change.objects.filter(dataownercode=dataownercode,
                                              line=line_qry[0],
                                              operatingday=operatingday,
                                              is_recovered=True).delete()

        else:
            raise ValidationError(_("Geen geldige lijn geselecteerd"))

        valid_journeys += 1

        return valid_journeys

    def clean_all_lines(self, operatingday, dataownercode):
        valid_journeys = 0

        database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                      is_alllines=True,
                                                      operatingday=operatingday,
                                                      is_recovered=False)

        if database_alllines:
            raise ValidationError(_("De gehele vervoerder is al aangepast."))

        # delete recovered if query is the same.
        Kv17Change.objects.filter(dataownercode=dataownercode,
                                  is_alllines=True,
                                  is_recovered=True,
                                  operatingday=operatingday).delete()

        valid_journeys += 1

        return valid_journeys

    def save(self, force_insert=False, force_update=False, commit=True):
        ''' Save each of the journeys in the model. This is a disaster, we return the XML
        TODO: Figure out a better solution fo this! '''
        operatingday = parse_date(self.data['operatingday'])

        if 'Alle ritten' in self.data['journeys']:
            xml_output = self.save_all_journeys(operatingday)
        elif 'Hele vervoerder' in self.data['lines']:
            xml_output = self.save_all_lines(operatingday)
        else:
            xml_output = self.save_journeys(operatingday)

        return xml_output

    def save_all_lines(self, operatingday):
        xml_output = []

        self.instance.pk = None
        self.instance.is_alllines = True
        self.instance.operatingday = operatingday
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

    def save_all_journeys(self, operatingday):
        xml_output = []

        for line in self.data['lines'].split(',')[0:-1]:
            qry = Kv1Line.objects.filter(id=line)
            if qry.count() == 1:
                self.instance.pk = None
                self.instance.is_alljourneysofline = True
                self.instance.line = qry[0]
                self.instance.operatingday = operatingday
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


    class Meta(object):
        model = Kv17Change
        exclude = ['dataownercode', 'operatingday', 'line', 'journey', 'is_recovered', 'reinforcement']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Kv17ChangeForm, self).__init__(*args, **kwargs)

        DAYS = [[str(d['date'].strftime('%Y-%m-%d')), str(d['date'].strftime('%d-%m-%Y'))] for d in
                Kv1JourneyDate.objects.all()
                    .filter(date__gte=datetime.today() - timedelta(days=1))
                    .values('date')
                    .distinct('date')
                    .order_by('date')]

        OPERATING_DAY = DAYS[((datetime.now().hour < 4) * -1) + 1] if len(DAYS) > 1 else None
        self.fields['operatingday'].choices = DAYS
        self.fields['operatingday'].initial = OPERATING_DAY

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(_('Datum'),
                               'operatingday'
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
