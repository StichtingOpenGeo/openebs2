import floppyforms as forms
from models import Kv15Stopmessage

class Kv15StopMessageForm(forms.ModelForm):
    class Meta:
        model = Kv15Stopmessage
        widgets = {
            'messagecontent': forms.Textarea
        }