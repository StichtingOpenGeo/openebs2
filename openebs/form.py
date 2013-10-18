import floppyforms as forms
from utils.widgets import DatePicker
from models import Kv15Stopmessage

class Kv15StopMessageForm(forms.ModelForm):
    class Meta:
        model = Kv15Stopmessage
        exclude = ['messagecodenumber', 'isdeleted', 'id', 'dataownercode']
        widgets = {
            'messagecodedate' : DatePicker,
            'messagecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'reasoncontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'})
        }