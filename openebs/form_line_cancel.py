from builtins import object
import logging
from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date
import floppyforms.__future__ as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1JourneyDate, Kv1Line
from kv15.enum import REASONTYPE, SUBREASONTYPE, ADVICETYPE, SUBADVICETYPE
from openebs.models import Kv17ChangeLine, Kv17ChangeLineChange
from datetime import datetime, timedelta, time


log = logging.getLogger('openebs.forms')


class ChangeLineCancelCreateForm(forms.ModelForm):
    # This is duplication, but should work

    DAYS = [[str(d['date'].strftime('%Y-%m-%d')), str(d['date'].strftime('%d-%m-%Y'))] for d in Kv1JourneyDate.objects.all() \
        .filter(date__gte=datetime.today() - timedelta(days=1)) \
        .values('date') \
        .distinct('date') \
        .order_by('date')]

    current = [str(datetime.today().strftime('%Y-%m-%d')), str(datetime.today().strftime('%d-%m-%Y'))]
    DAYS.append(current) if current not in DAYS else None
    OPERATING_DAY = DAYS[((datetime.now().hour < 4) * -1) + 1] if len(DAYS) > 1 else current[1]

    operatingday = forms.ChoiceField(choices=DAYS, label=_("Datum"), initial=OPERATING_DAY, required=False)
    begintime_part = forms.TimeField(label=_('Ingangstijd'), required=False, widget=forms.TimeInput(format='%H:%M:%S'))
    endtime_part = forms.TimeField(label=_('Eindtijd'), required=False, widget=forms.TimeInput(format='%H:%M:%S'))
    reasontype = forms.ChoiceField(choices=REASONTYPE, label=_("Type oorzaak"), required=False)
    subreasontype = forms.ChoiceField(choices=SUBREASONTYPE, label=_("Oorzaak"), required=False)
    reasoncontent = forms.CharField(max_length=255, label=_("Uitleg oorzaak"), required=False,
                                    widget=forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}))
    advicetype = forms.ChoiceField(choices=ADVICETYPE, label=_("Type advies"), required=False)
    subadvicetype = forms.ChoiceField(choices=SUBADVICETYPE, label=_("Advies"), required=False)
    advicecontent = forms.CharField(max_length=255, label=_("Uitleg advies"), required=False,
                                    widget=forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}))

    def clean(self):
        cleaned_data = super(ChangeLineCancelCreateForm, self).clean()
        operatingday = parse_date(self.data['operatingday'])
        begintime = None
        if self.data['begintime_part'] != '':
            hh, mm = self.data['begintime_part'].split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))

        if 'CancelAll' in self.data:
            if Kv17ChangeLine.objects.filter(line__isnull=True, is_recovered=False, operatingday=operatingday, begintime=begintime).count() != 0:
                raise ValidationError(_("Deze operatie is al gepland."))

            return cleaned_data

        if 'lijnen' not in self.data:
            raise ValidationError(_("Een of meer geselecteerde lijnen zijn ongeldig"))

        if self.data['endtime_part'] != '':
            hh_e, mm_e = self.data['endtime_part'].split(':')
            endtime = time(int(hh_e), int(mm_e))
            if begintime and endtime < time(int(hh), int(mm)): # if endtime before begintime
                if endtime >= time(6, 0): # and after 6 am: validation error
                    raise ValidationError(_("Eindtijd valt op volgende operationele dag"))

        valid_lines = 0
        for line in self.data['lijnen'].split(',')[0:-1]:
            if Kv17ChangeLine.objects.filter(line__pk=line, \
                                             line=line, \
                                             operatingday=operatingday, \
                                             begintime=begintime, \
                                             is_recovered=False).count() != 0:
                raise ValidationError(_("Een of meer geselecteerde lijnen zijn al aangepast"))
            valid_lines += 1
        if valid_lines == 0:
            raise ValidationError(_("Er zijn geen lijnen geselecteerd om op te heffen"))

        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        ''' Save each of the lines in the model. This is a disaster, we return the XML
        TODO: Figure out a better solution fo this! '''
        xml_output = []

        # splits begintime / endtime in HH:MM als het niet leeg is, dat optellen bij operatingdate
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

        if 'CancelAll' in self.data:
            self.instance.pk = None
            self.instance.line = None
            self.instance.operatingday = operatingday
            self.instance.begintime = begintime
            self.instance.endtime = endtime

            self.instance.is_cancel = True
            self.instance.save()

            # Add details
            if self.data['reasontype'] != '0' or self.data['advicetype'] != '0':
                Kv17ChangeLineChange(change=self.instance,
                                     reasontype=self.data['reasontype'],
                                     subreasontype=self.data['subreasontype'],
                                     reasoncontent=self.data['reasoncontent'],
                                     advicetype=self.data['advicetype'],
                                     subadvicetype=self.data['subadvicetype'],
                                     advicecontent=self.data['advicecontent']).save()

            xml_output.append(self.instance.to_xml())

        else:
            for line in self.data['lijnen'].split(',')[0:-1]:
                qry = Kv1Line.objects.filter(id=line)
                if qry.count() == 1:
                    self.instance.pk = None
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
                            Kv17ChangeLineChange(change=self.instance,
                                              reasontype=self.data['reasontype'],
                                              subreasontype=self.data['subreasontype'],
                                              reasoncontent=self.data['reasoncontent'],
                                              advicetype=self.data['advicetype'],
                                              subadvicetype=self.data['subadvicetype'],
                                              advicecontent=self.data['advicecontent']).save()

                        xml_output.append(self.instance.to_xml())
                    else:
                        log.error("Oops! mismatch between dataownercode of line (%s) and of user (%s) when saving journey cancel" %
                                  (self.instance.line.dataownercode, self.instance.dataownercode))
                else:
                    log.error("Failed to find line %s" % line)

        log.error(xml_output)
        return xml_output

    class Meta(object):
        model = Kv17ChangeLine
        exclude = [ 'dataownercode', 'line', 'is_recovered']

    def __init__(self, *args, **kwargs):
        super(ChangeLineCancelCreateForm, self).__init__(*args, **kwargs)
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
