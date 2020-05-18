from builtins import object
import logging
from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div, Hidden
from django.utils.timezone import now, make_aware, utc
import floppyforms.__future__ as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1Line, Kv1Stop, Kv1Journey, Kv1JourneyDate
from kv15.enum import REASONTYPE, SUBREASONTYPE, ADVICETYPE, SUBADVICETYPE
from openebs.models import Kv15Stopmessage, Kv15Scenario, Kv15ScenarioMessage, Kv17Change, get_end_service
from openebs.models import Kv17JourneyChange
from utils.time import get_operator_date
from datetime import datetime, time, timedelta
from django.db.models import Q

from django.utils.dateparse import parse_date


log = logging.getLogger('openebs.forms')


class Kv15StopMessageForm(forms.ModelForm):
    def clean(self):
        # TODO Move _all_ halte parsing here!
        ids = []
        for halte in self.data['haltes'].split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    ids.append(stop.pk)
                else:
                    raise ValidationError(_("Datafout: halte niet gevonden in database. Meld dit bij een beheerder."))
        if len(ids) == 0:
            raise ValidationError(_("Selecteer minimaal een halte"))
        else:
            return self.cleaned_data

    def clean_messagecontent(self):
        # Improve: Strip spaces from message
        if ('messagecontent' not in self.cleaned_data or self.cleaned_data['messagecontent'] is None or len(
                self.cleaned_data['messagecontent']) < 1) \
                and self.cleaned_data['messagetype'] != 'OVERRULE':
            raise ValidationError(_("Bericht mag niet leeg zijn"))
        return self.cleaned_data['messagecontent']

    class Meta(object):
        model = Kv15Stopmessage
        exclude = ['messagecodenumber', 'status', 'stops', 'messagecodedate', 'isdeleted', 'id', 'dataownercode',
                   'user']
        widgets = {
            'messagecontent': forms.Textarea(attrs={'cols': 50, 'rows': 6, 'class': 'col-lg-6', 'maxlength': 255}),
            'reasoncontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority': forms.RadioSelect,
            'messagedurationtype': forms.RadioSelect,
            'messagetype': forms.RadioSelect,
            'messagestarttime': forms.DateTimeInput,
            'messageendtime': forms.DateTimeInput,
            'reasontype': forms.RadioSelect,
            'subreasontype': forms.Select,
            'effecttype': forms.RadioSelect,
            'subeffecttype': forms.Select,
            'measuretype': forms.RadioSelect,
            'submeasuretype': forms.Select,
            'advicetype': forms.RadioSelect,
            'subadvicetype': forms.Select,
            'messagetimestamp': forms.DateTimeInput
        }

    def __init__(self, *args, **kwargs):
        super(Kv15StopMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(HTML('<span class="charcount badge badge-success pull-right">0</span>'),
                Field('messagecontent'), css_class='countwrapper'),
            'messagestarttime',
            'messageendtime',
            Accordion(
                AccordionGroup(_('Bericht instellingen'),
                               'messagepriority',
                               'messagetype',
                               'messagedurationtype'
                               ),
                AccordionGroup(_('Oorzaak'),
                               'reasontype',
                               'subreasontype',
                               'reasoncontent'
                               ),
                AccordionGroup(_('Effect'),
                               'effecttype',
                               'subeffecttype',
                               'effectcontent'
                               ),
                AccordionGroup(_('Gevolg'),
                               'measuretype',
                               'submeasuretype',
                               'measurecontent'
                               ),
                AccordionGroup(_('Advies'),
                               'advicetype',
                               'subadvicetype',
                               'advicecontent'
                               )
            )
        )


class Kv15ScenarioForm(forms.ModelForm):
    class Meta(object):
        model = Kv15Scenario
        exclude = ['dataownercode']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
        }

    def __init__(self, *args, **kwargs):
        super(Kv15ScenarioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form_horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'


class Kv15ScenarioMessageForm(forms.ModelForm):

    def clean(self):
        # TODO Move _all_ halte parsing here! Also duplicated with code above
        ids = []
        for halte in self.data['haltes'].split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    ids.append(stop.pk)
        qry = Kv1Stop.objects.filter(kv15scenariostop__message__scenario=self.data['scenario'], pk__in=ids)
        if self.instance.pk is not None:  # Exclude ourselves if we've been saved
            qry = qry.exclude(kv15scenariostop__message=self.instance.pk)

        if qry.count() > 0:
            # Check that this stop isn't already in a messages for this scenario. If not, write a nice message
            out = ""
            for stop in qry:
                out += "%s, " % stop.name
            raise ValidationError(_("Halte(s) ' %s ' bestaan al voor dit scenario") % out)
        elif len(ids) == 0:
            # Select at least one stop for a message
            raise ValidationError(_("Selecteer minimaal een halte"))
        else:
            return self.cleaned_data

    class Meta(object):
        model = Kv15ScenarioMessage
        exclude = ['dataownercode']
        widgets = {
            'scenario': forms.HiddenInput,
            'messagecontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'reasoncontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'class': 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority': forms.RadioSelect,
            'messagetype': forms.RadioSelect,
            'messagedurationtype': forms.RadioSelect,
            'messagestarttime': forms.DateTimeInput,
            'messageendtime': forms.DateTimeInput,
            'reasontype': forms.RadioSelect,
            'subreasontype': forms.Select,
            'effecttype': forms.RadioSelect,
            'subeffecttype': forms.Select,
            'measuretype': forms.RadioSelect,
            'submeasuretype': forms.Select,
            'advicetype': forms.RadioSelect,
            'subadvicetype': forms.Select
        }

    def __init__(self, *args, **kwargs):
        super(Kv15ScenarioMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'scenario',
            Div(HTML('<span class="charcount badge badge-success pull-right">0</span>'),
                Field('messagecontent'), css_class='countwrapper'),
            Accordion(
                AccordionGroup(_('Bericht instellingen'),
                               'messagepriority',
                               'messagetype',
                               'messagedurationtype'
                               ),
                AccordionGroup(_('Oorzaak'),
                               'reasontype',
                               'subreasontype',
                               'reasoncontent'
                               ),
                AccordionGroup(_('Effect'),
                               'effecttype',
                               'subeffecttype',
                               'effectcontent'
                               ),
                AccordionGroup(_('Gevolg'),
                               'measuretype',
                               'submeasuretype',
                               'measurecontent'
                               ),
                AccordionGroup(_('Advies'),
                               'advicetype',
                               'subadvicetype',
                               'advicecontent'
                               )
            )
        )


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
        operatingday = parse_date(self.data['operatingday'])
        if operatingday is None:
            raise ValidationError(_("Er staan geen ritten in de database"))

        begintime = None  # datetime.utcnow().replace(tzinfo=utc)
        if self.data['begintime_part'] != '':
            hh, mm = self.data['begintime_part'].split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))

        endtime = None
        if self.data['endtime_part'] != '':
            hh_e, mm_e = self.data['endtime_part'].split(':')
            #endtime = time(int(hh_e), int(mm_e))
            endtime = make_aware(datetime.combine(operatingday, time(int(hh_e), int(mm_e))))
            if begintime > endtime:  # if endtime before begintime
                endtime = endtime + timedelta(days=1)  # endtime is next day
                if endtime.time() >= time(6, 0):  # and after 6 am: validation error
                    raise ValidationError(_("Eindtijd valt op volgende operationele dag"))

        dataownercode = self.user.userprofile.company

        cleaned_data = super(Kv17ChangeForm, self).clean()
        if 'journeys' not in self.data:
            raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig"))

        valid_journeys = 0
        if 'Alle ritten' in self.data['journeys']:
            if 'lines' in self.data:
                if self.data['lines'] != '':
                    for line in self.data['lines'].split(',')[0:-1]:
                        line_qry = Kv1Line.objects.filter(pk=line)
                        if line_qry.count() == 0:
                            raise ValidationError(_("Geen lijn gevonden."))

                        """
                        Kv17Change.objects.filter(Q(begintime__gte=begintime) & Q(begintime__lte=endtime),
                                                     is_alljourneysofline=True, line=line_qry[0],
                                                     operatingday=operatingday,
                                                     is_recovered=True).delete()
                        """
                        if begintime:
                            if endtime:
                                if Kv17Change.objects.filter(Q(begintime__lte=begintime) & Q(begintime__lte=endtime),
                                                             dataownercode=dataownercode,
                                                             is_alljourneysofline=True, line=line_qry[0],
                                                             operatingday=operatingday,
                                                             is_recovered=False).count() != 0:
                                    raise ValidationError(_("Een of meer geselecteerde lijnen zijn al aangepast"))
                            else:
                                if Kv17Change.objects.filter(Q(begintime__lte=begintime),
                                                             dataownercode=dataownercode,
                                                             is_alljourneysofline=True, line=line_qry[0],
                                                             operatingday=operatingday,
                                                             is_recovered=False).count() != 0:
                                    raise ValidationError(_("Een of meer geselecteerde lijnen zijn al aangepast"))
                        else:
                            begintime = datetime.utcnow().replace(tzinfo=utc)
                            if Kv17Change.objects.filter(is_alljourneysofline=True, line=line_qry[0],
                                                         dataownercode=dataownercode,
                                                         operatingday=operatingday,
                                                         begintime__lte=begintime,
                                                         is_recovered=False).count() != 0:
                                    raise ValidationError(_("Een of meer geselecteerde lijnen zijn al aangepast"))
                else:
                    raise ValidationError(_("Er werd geen lijn geselecteerd"))

                valid_journeys -= 1
            else:
                raise ValidationError(_("Een of meer geselecteerde lijnen zijn ongeldig"))

        elif 'Hele vervoerder' in self.data['lines']:
            if begintime:
                if endtime:
                    #Kv17Change.objects.filter(Q(begintime__lte=begintime) & Q(begintime__lte=endtime),
                    #                          dataownercode=dataownercode,
                    #                          is_alllines=True,
                    #                          is_recovered=True,
                    #                          operatingday=operatingday).delete()
                    if Kv17Change.objects.filter(Q(begintime__lte=begintime) & Q(begintime__lte=endtime),
                                                 dataownercode=dataownercode,
                                                 is_alllines=True,
                                                 is_recovered=False,
                                                 operatingday=str(operatingday)).count() != 0:
                        raise ValidationError(_("Deze operatie is al gepland."))
                else:
                    Kv17Change.objects.filter(begintime__lte=begintime,
                                              dataownercode=dataownercode,
                                              is_alllines=True,
                                              is_recovered=True,
                                              operatingday=operatingday).delete()
                    if Kv17Change.objects.filter(begintime__lte=begintime,
                                                 dataownercode=dataownercode,
                                                 is_alllines=True,
                                                 is_recovered=False,
                                                 operatingday=operatingday).count() != 0:
                        raise ValidationError(_("Deze operatie is al gepland."))
            else:
                if Kv17Change.objects.filter(dataownercode=dataownercode,
                                             is_alllines=True,
                                             is_recovered=False,
                                             operatingday=operatingday).count() != 0:
                    raise ValidationError(_("Deze operatie is al gepland."))
            valid_journeys -= 1

        else:
            for journey in self.data['journeys'].split(',')[0:-1]:
                journey_qry = Kv1Journey.objects.filter(pk=journey, dates__date=operatingday)
                if journey_qry.count() == 0:
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn ongeldig."))

                if Kv17Change.objects.filter(dataownercode=dataownercode,
                                             journey__pk=journey,
                                             line=journey_qry[0].line,
                                             operatingday=operatingday,
                                             is_recovered=False).count() != 0:
                    raise ValidationError(_("Een of meer geselecteerde ritten zijn al aangepast."))

                if Kv17Change.objects.filter(Q(is_alljourneysofline=True) & Q(line=journey_qry[0].line) | Q(is_alllines=True),
                                             dataownercode=dataownercode,
                                             operatingday=operatingday,
                                             is_recovered=False).count() != 0:
                    raise ValidationError(_("Deze lijn is al opgeheven."))

                Kv17Change.objects.filter(journey__pk=journey,
                                          dataownercode=dataownercode,
                                          line=journey_qry[0].line,
                                          operatingday=operatingday,
                                          is_recovered=True).delete()
            valid_journeys += 1

        if valid_journeys == 0:
            raise ValidationError(_("Er zijn geen ritten geselecteerd om op te heffen"))

        return cleaned_data

    def save_all_lines(self, force_insert=False, force_update=False, commit=True):
        xml_output = []
        operatingday = parse_date(self.data['operatingday'])
        begintime = None
        if self.data['begintime_part'] != '':
            hh, mm = self.data['begintime_part'].split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))

        endtime = None
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

        self.instance.pk = None
        self.instance.is_alllines = True
        self.instance.operatingday = operatingday
        self.instance.begintime = begintime
        self.instance.endtime = endtime
        self.instance.is_cancel = True

        # Unfortunately, we can't place this any earlier, because we don't have the dataownercode there
        if self.instance.dataownercode:
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

    def save_all_journeys(self, force_insert=False, force_update=False, commit=True):
        xml_output = []
        operatingday = get_operator_date()
        begintime = None
        if self.data['begintime_part'] != '':
            hh, mm = self.data['begintime_part'].split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))

        endtime = None
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

        return xml_output

    def save_journey(self, force_insert=False, force_update=False, commit=True):
        xml_output = []

        for journey in self.data['journeys'].split(',')[0:-1]:
            qry = Kv1Journey.objects.filter(id=journey, dates__date=get_operator_date())
            if qry.count() == 1:
                self.instance.pk = None
                self.instance.journey = qry[0]
                self.instance.line = qry[0].line
                self.instance.operatingday = get_operator_date()
                self.instance.is_cancel = True
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

    def save(self, force_insert=False, force_update=False, commit=True):
        ''' Save each of the mutations in the model.'''

        if 'Alle ritten' in self.data['journeys']:
            xml_output = self.save_all_journeys(force_insert, force_update, commit)
        elif 'Hele vervoerder' in self.data['lines']:
            xml_output = self.save_all_lines(force_insert, force_update, commit)
        else:
            xml_output = self.save_journey(force_insert, force_update, commit)

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
                               )
            )
        )


class PlanScenarioForm(forms.Form):
    messagestarttime = forms.DateTimeField(label=_("Begin"), initial=now)
    messageendtime = forms.DateTimeField(label=_("Einde"), initial=get_end_service)

    def clean(self):
        data = super(PlanScenarioForm, self).clean()
        if data['messageendtime'] <= data['messagestarttime']:
            raise ValidationError(_("Einde bericht moet na begin zijn"))
        return data

    def __init__(self, *args, **kwargs):
        super(PlanScenarioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = 'scenario_plan'
        self.helper.layout = Layout(
            # Put in two columns
            Div(Div(Field('messagestarttime'), css_class="col-sm-6 col-lg-6"),
                Div(Field('messageendtime'), css_class="col-sm-6 col-lg-6"),
                css_class="row"),
            Submit('submit', _("Plan alle berichten in"))
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
