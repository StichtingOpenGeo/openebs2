from crispy_forms.bootstrap import AccordionGroup, Accordion, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div
import floppyforms as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1Stop
from models import Kv15Stopmessage, Kv15Scenario, Kv15ScenarioMessage


class Kv15StopMessageForm(forms.ModelForm):
    class Meta:
        model = Kv15Stopmessage
        exclude = ['messagecodenumber', 'stops', 'messagecodedate', 'isdeleted', 'id', 'dataownercode', 'user']
        widgets = {
            'messagecontent': forms.Textarea(attrs={'cols' : 50, 'rows' : 4, 'class' : 'col-lg-6', 'maxlength':255 }),
            'reasoncontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority' : forms.RadioSelect,
            'messagedurationtype' : forms.RadioSelect,
            'messagetype' : forms.RadioSelect,
            'messagestarttime' : forms.DateTimeInput,
            'messageendtime' : forms.DateTimeInput,
            'reasontype' : forms.RadioSelect,
            'subreasontype' : forms.Select,
            'effecttype' : forms.RadioSelect,
            'subeffecttype' : forms.Select,
            'measuretype' : forms.RadioSelect,
            'submeasuretype' : forms.Select,
            'advicetype' : forms.RadioSelect,
            'subadvicetype' : forms.Select,
            'messagetimestamp' : forms.DateTimeInput
        }


    def __init__(self, *args, **kwargs):
        super(Kv15StopMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(HTML('<span class="charcount badge badge-success pull-right">0</span>'),
                Field('messagecontent'),
                css_class='countwrapper'),
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
    class Meta:
        model = Kv15Scenario
        widgets = {
            'description': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
        }

class Kv15ScenarioMessageForm(forms.ModelForm):

    def clean(self):
        # TODO Move _all_ halte parsing here!
        ids = []
        for halte in self.data['haltes'].split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    ids.append(stop.pk)
        qry = Kv1Stop.objects.filter(kv15scenariostop__message__scenario=self.data['scenario'], pk__in=ids)
        if qry.count() > 0:
            out = ""
            for stop in qry:
                out += "%s, " % stop.name
            raise ValidationError(_("Halte(s) ' %s ' bestaan al voor dit scenario") % out)
        else:
            return self.cleaned_data

    class Meta:
        model = Kv15ScenarioMessage
        exclude = ['dataownercode']
        widgets = {
            'scenario': forms.HiddenInput,
            'messagecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'reasoncontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority' : forms.RadioSelect,
            'messagetype' : forms.RadioSelect,
            'messagedurationtype' : forms.RadioSelect,
            'messagestarttime' : forms.DateTimeInput,
            'messageendtime' : forms.DateTimeInput,
            'reasontype' : forms.RadioSelect,
            'subreasontype' : forms.Select,
            'effecttype' : forms.RadioSelect,
            'subeffecttype' : forms.Select,
            'measuretype' : forms.RadioSelect,
            'submeasuretype' : forms.Select,
            'advicetype' : forms.RadioSelect,
            'subadvicetype' : forms.Select
        }

    def __init__(self, *args, **kwargs):
        super(Kv15ScenarioMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'scenario',
            'messagecontent',
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