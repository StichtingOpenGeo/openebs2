from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
import floppyforms as forms
from utils.widgets import DatePicker
from models import Kv15Stopmessage, Kv15Scenario, Kv15ScenarioMessage


class Kv15StopMessageForm(forms.ModelForm):
    class Meta:
        model = Kv15Stopmessage
        exclude = ['messagecodenumber', 'stops', 'messagedurationtype', 'messagecodedate', 'isdeleted', 'id', 'dataownercode', 'user']
        widgets = {
            'messagecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'reasoncontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority' : forms.RadioSelect,
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
        #self.helper.form_class = 'form'
        #self.helper.form_method = 'post'
        #self.helper.form_action = 'msg_add'
        self.helper.layout = Layout(
            Field('haltes'),
            'messagecontent',
            'messagestarttime',
            'messageendtime',
            Accordion(
                AccordionGroup('Oorzaak',
                   'reasontype',
                   'subreasontype',
                   'reasoncontent'
                ),
                AccordionGroup('Effect',
                   'effecttype',
                   'subeffecttype',
                   'effectcontent'
                ),
                AccordionGroup('Gevolg',
                   'measuretype',
                   'submeasuretype',
                   'measurecontent'
                ),
                AccordionGroup('Advies',
                   'advicetype',
                   'subadvicetype',
                   'advicecontent'
                )
            )
        )

        #self.helper.add_input(Submit('submit', 'Toevoegen'))

class Kv15ScenarioForm(forms.ModelForm):
    class Meta:
        model = Kv15Scenario
        widgets = {
            'description': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
        }

class Kv15ScenarioMessageForm(forms.ModelForm):
    class Meta:
        model = Kv15ScenarioMessage
        exclude = ['scenario', 'dataownercode']
        widgets = {
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
