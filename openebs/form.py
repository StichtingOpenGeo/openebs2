from builtins import object
import logging
from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div, Hidden
from django.utils.timezone import now, is_aware, make_aware
import floppyforms.__future__ as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1Stop, Kv1Journey
from kv15.enum import REASONTYPE, SUBREASONTYPE, ADVICETYPE, SUBADVICETYPE
from openebs.models import Kv15Stopmessage, Kv15Scenario, Kv15ScenarioMessage, Kv17Change, get_end_service
from openebs.models import Kv17JourneyChange
from utils.time import get_operator_date
from datetime import datetime

log = logging.getLogger('openebs.forms')


class Kv15StopMessageForm(forms.ModelForm):
    def clean(self):
        # TODO Move _all_ halte parsing here!

        datetimevalidation = []
        try:
            datetime.strptime(self.data['messagestarttime'], "%d-%m-%Y %H:%M:%S")
        except:
            datetimevalidation.append(_("Voer een geldige begintijd in (dd-mm-jjjj uu:mm:ss)"))
            pass

        try:
            endtime = datetime.strptime(self.data['messageendtime'], "%d-%m-%Y %H:%M:%S")
            if not is_aware(endtime):
                endtime = make_aware(endtime)
        except:
            datetimevalidation.append(_("Voer een geldige eindtijd in (dd-mm-jjjj uu:mm:ss)"))
            pass

        if len(datetimevalidation) == 2:
            raise ValidationError(_("Voer een geldige begin- en eindtijd in (dd-mm-jjjj uu:mm:ss)"))
        elif len(datetimevalidation) == 1:
            raise ValidationError(datetimevalidation[0])

        current = datetime.now()
        if not is_aware(current):
            current = make_aware(current)

        valid_ids = []
        nonvalid_ids = []
        for halte in self.data['haltes'].split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    valid_ids.append(stop.pk)
                else:
                    nonvalid_ids.append(halte)

        if len(nonvalid_ids) != 0:
            log.warning("Ongeldige haltes: %s" % ', '.join(nonvalid_ids))
        if len(valid_ids) == 0 and len(nonvalid_ids) != 0:
            raise ValidationError(_("Er werd geen geldige halte geselecteerd."))
        elif len(valid_ids) == 0:
            raise ValidationError(_("Selecteer minimaal een halte."))
        elif current > endtime:
            raise ValidationError(_("Eindtijd van bericht ligt in het verleden"))
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
    """ Make sure every scenario has a title / name """
    def clean(self):
        if self.data['name'].strip() == '':
            raise ValidationError(_("Naam scenario mag niet leeg zijn."))
        else:
            return self.cleaned_data

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
        elif ('messagecontent' not in self.cleaned_data or self.cleaned_data['messagecontent'] is None or len(
                self.cleaned_data['messagecontent'].strip()) == 0) \
                and self.cleaned_data['messagetype'] != 'OVERRULE':
            raise ValidationError(_("Bericht mag niet leeg zijn"))
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


class PlanScenarioForm(forms.Form):
    messagestarttime = forms.DateTimeField(label=_("Begin"), initial=now)
    messageendtime = forms.DateTimeField(label=_("Einde"), initial=get_end_service)

    def clean(self):
        data = super(PlanScenarioForm, self).clean()
        if 'messagestarttime' not in data and 'messageendtime' not in data:
            raise ValidationError(_("Voer een geldige begin- en eindtijd in"))

        if 'messagestarttime' not in data:
            raise ValidationError(_("Voer een geldige begintijd in"))

        if 'messageendtime' not in data:
            raise ValidationError(_("Voer een geldige eindtijd in"))

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
