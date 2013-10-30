import floppyforms as forms

class DatePicker(forms.DateInput):
    # From the floppyforms example
    template_name = 'floppyforms/widgets/datepicker.html'

    class Media:
        js = (
            'js/jquery-ui.min.js',
        )
        css = {
            'all': (
                'css/jquery-ui.css',
            )
        }
