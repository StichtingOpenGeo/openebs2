import floppyforms as forms
from utils.widgets import DatePicker
from models import Kv15Stopmessage, Kv15Scenario


class Kv15StopMessageForm(forms.ModelForm):
    class Meta:
        model = Kv15Stopmessage
        exclude = ['messagecodenumber', 'isdeleted', 'id', 'dataownercode', 'user']
        widgets = {
            'messagecodedate' : DatePicker,
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
            'subadvicetype' : forms.Select,
            'messagetimestamp' : forms.DateTimeInput
        }

class Kv15ScenarioForm(forms.ModelForm):
    class Meta:
        model = Kv15Scenario
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
            'subadvicetype' : forms.Select,
            'messagetimestamp' : forms.DateTimeInput
        }
