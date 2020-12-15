from builtins import object
from dateutil.tz import tzlocal
import logging
import re
from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div#, Hidden
from django.utils.timezone import now
import floppyforms.__future__ as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1Stop
from openebs.models import Kv15Stopmessage, Kv15Scenario, Kv15ScenarioMessage, get_end_service, MessageStatus

import xml.etree.ElementTree as ET
from dateutil.parser import parse
from kv15.enum import MESSAGEPRIORITY, MESSAGETYPE, MESSAGEDURATIONTYPE

log = logging.getLogger('openebs.forms')


class Kv15StopMessageForm(forms.ModelForm):
    def clean(self):
        # TODO Move _all_ halte parsing here!
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


class Kv15ImportForm(forms.Form):
    def clean(self):
        if 'action' not in self.data:
            xml = self.data['import-text']
            if len(xml) == 0:
                raise ValidationError(_("Bericht mag niet leeg zijn."))

            xml = re.sub(r'\sxmlns="[^"]+"', '', xml, count=1)

            try:
                root = ET.fromstring(xml)
            except:
                raise ValidationError(_("Het bericht is geen geldig XML-bericht."))

            try:
                root.find('STOPMESSAGE')
            except:
                raise ValidationError(_("Bericht bevat geen 'Stopmessage'."))

            kv15stopmessages = []
            if not root.findall(".//STOPMESSAGE"):
                raise ValidationError(_("Bericht is geen geldig XML-bericht."))
            for message in root.findall(".//STOPMESSAGE"):
                """ Check if all required items are present and valid """
                try:
                    dataownercode = message.find('dataownercode').text
                except:
                    raise ValidationError(_("Bericht bevat geen dataownercode."))
                if self.user.userprofile.company != dataownercode and not self.user.is_staff:
                    raise ValidationError(_("Dataownercode in bericht komt niet overeen met gebruikersprofiel."))

                try:
                    messagecodedate = message.find('messagecodedate').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagecodedate."))
                try:
                    parse(messagecodedate, fuzzy=False)
                except:
                    raise ValidationError(_("Bericht bevat een ongeldige messagecodedate."))

                try:
                    messagecodenumber = message.find('messagecodenumber').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagecodenumber."))

                # Check for duplicate key (Dataownercode, messagecodedate, messagecodenumber)
                if Kv15Stopmessage.objects.filter(dataownercode=dataownercode, messagecodedate=messagecodedate,
                                                  messagecodenumber=messagecodenumber).count() != 0:
                    raise ValidationError(_("De combinatie dataownercode, messagecodedate en messagecodenumber bestaat al."))

                try:
                    userstopcodes = []
                    codes = message.findall('./userstopcodes//userstopcode')
                    for code in codes:
                        userstopcodes.append(dataownercode+"_"+code.text)
                    if len(userstopcodes) == 0:
                        raise ValidationError(_("Bericht bevat geen userstopcodes."))
                except:
                    raise ValidationError(_("Bericht bevat geen userstopcodes."))
                stops = ','.join(userstopcodes)
                valid_stops = Kv1Stop.find_stops_from_haltes(stops)
                if len(valid_stops) == 0:
                    raise ValidationError(_("Bericht bevat geen geldige userstopcodes"))

                try:
                    messagepriority = message.find('messagepriority').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagepriority."))
                if not (any(messagepriority in i for i in MESSAGEPRIORITY)):
                    raise ValidationError(_("Bericht bevat een ongeldige messagepriority"))

                try:
                    messagetype = message.find('messagetype').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagetype."))
                if not (any(messagetype in i for i in MESSAGETYPE)):
                    raise ValidationError(_("Bericht bevat een ongeldige messagetype"))
                if messagetype != 'OVERRULE':
                    messagecontent = message.find('messagecontent').text
                    if len(messagecontent) == 0:
                        raise ValidationError(_("Bericht bevat lege messagecontent."))

                try:
                    messagedurationtype = message.find('messagedurationtype').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagedurationtype."))
                if not (any(messagedurationtype in i for i in MESSAGEDURATIONTYPE)):
                    raise ValidationError(_("Bericht bevat een ongeldige messagedurationtype"))

                try:
                    messagestarttime = message.find('messagestarttime').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagestarttime."))
                try:
                    starttime = parse(messagestarttime)
                except:
                    raise ValidationError(_("Bericht bevat een ongeldige messagestarttime"))

                endtime = None
                try:
                    messageendtime = message.find('messageendtime').text
                    try:
                         endtime = parse(messageendtime)
                    except:
                         raise ValidationError(_("Bericht bevat een ongeldige messageendtime"))
                except:
                    pass  # messageendtime is not required
                # try:
                #     endtime = parse(messageendtime)
                # except:
                #     raise ValidationError(_("Bericht bevat een ongeldige messageendtime"))

                try:
                    messagetimestamp = message.find('messagetimestamp').text
                except:
                    raise ValidationError(_("Bericht bevat geen messagetimestamp."))
                try:
                    timestamp = parse(messagetimestamp)
                except:
                    raise ValidationError(_("Bericht bevat een ongeldige messagetimestamp"))

                kv15stopmessage = Kv15Stopmessage()
                kv15stopmessage.messagecodenumber = messagecodenumber
                kv15stopmessage.messagepriority = messagepriority
                kv15stopmessage.dataownercode = dataownercode
                kv15stopmessage.messagetimestamp = timestamp
                kv15stopmessage.messagecodedate = messagecodedate
                kv15stopmessage.messagetype = messagetype
                kv15stopmessage.messagecontent = messagecontent
                kv15stopmessage.messagedurationtype = messagedurationtype

                kv15stopmessage.messagestarttime = starttime.replace(tzinfo=tzlocal())
                if endtime:
                    kv15stopmessage.messageendtime = endtime.replace(tzinfo=tzlocal())
                else:
                    kv15stopmessage.messageendtime = None

                kv15stopmessages.append({'kv15': kv15stopmessage, 'stops': valid_stops, 'user': self.user})

            self.cleaned_data = kv15stopmessages
            return kv15stopmessages

        else:
            self.import_data()
        #    if self.data['action'] == 'action_delete':
        #        return redirect('msg_delete')

    def import_data(self):
        """ save data from xml-message in the model.
        TODO; find a better way instead of repeating the clean function
        """
        xml = self.data['import-text']
        xml = re.sub(r'\sxmlns="[^"]+"', '', xml, count=1)
        root = ET.fromstring(xml)
        for message in root.findall(".//STOPMESSAGE"):
            kv15stopmessage = Kv15Stopmessage()

            kv15stopmessage.user = self.user
            kv15stopmessage.dataownercode = message.find('dataownercode').text
            kv15stopmessage.messagecodedate = parse(message.find('messagecodedate').text).replace(tzinfo=tzlocal())
            kv15stopmessage.messagecodenumber = message.find('messagecodenumber').text
            kv15stopmessage.messagepriority = message.find('messagepriority').text
            kv15stopmessage.messagetype = message.find('messagetype').text
            kv15stopmessage.messagetimestamp = parse(message.find('messagetimestamp').text).replace(tzinfo=tzlocal())
            kv15stopmessage.messagestarttime = parse(message.find('messagestarttime').text).replace(tzinfo=tzlocal())
            kv15stopmessage.messagecontent = message.find('messagecontent').text

            try:
                endtime = parse(message.find('messageendtime').text)
                kv15stopmessage.messageendtime = endtime.replace(tzinfo=tzlocal())
            except:
                kv15stopmessage.messageendtime = None  #TODO set as ending of day of starttime in imported message
            try:
                kv15stopmessage.reasontype = message.find('reasontype').text
            except:
                pass
            try:
                kv15stopmessage.subreasontype = message.find('subreasontype').text
            except:
                pass
            try:
                kv15stopmessage.reasoncontent = message.find('reasoncontent').text
            except:
                pass
            try:
                kv15stopmessage.effecttype = message.find('effecttype').text
            except:
                pass
            try:
                kv15stopmessage.subeffecttype = message.find('subeffecttype').text
            except:
                pass
            try:
                kv15stopmessage.effectcontent = message.find('subeffecttype').text
            except:
                pass
            try:
                kv15stopmessage.measuretype = message.find('measuretype').text
            except:
                pass
            try:
                kv15stopmessage.submeasuretype = message.find('submeasuretype').text
            except:
                pass
            try:
                kv15stopmessage.measurecontent = message.find('measurecontent').text
            except:
                pass
            try:
                kv15stopmessage.advicetype = message.find('advicetype').text
            except:
                pass
            try:
                kv15stopmessage.subadvicetype = message.find('subadvicetype').text
            except:
                pass
            try:
                kv15stopmessage.advicecontent = message.find('advicecontent').text
            except:
                pass

            self.kv15stopmessage = kv15stopmessage
            kv15stopmessage.save()

            # add stop data
            userstopcodes = []
            codes = message.findall('./userstopcodes//userstopcode')
            for code in codes:
                userstopcodes.append(kv15stopmessage.dataownercode + "_" + code.text)
            stops = ','.join(userstopcodes)
            valid_stops = Kv1Stop.find_stops_from_haltes(stops)
            for stop in valid_stops:
                kv15stopmessage.kv15messagestop_set.create(stopmessage=kv15stopmessage, stop=stop)

            return kv15stopmessage

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(Kv15ImportForm, self).__init__(*args, **kwargs)





