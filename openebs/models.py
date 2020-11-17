# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
from builtins import object
import logging
import os
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.timezone import now, datetime, get_current_timezone
from kv1.models import Kv1Stop, Kv1Line, Kv1Journey

from kv15.enum import *
from openebs2.settings import EXTERNAL_MESSAGE_USER_ID

log = logging.getLogger('openebs.views')


# TODO Move this
def get_end_service():
    # Hmm, this is GMT
    return (now() + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)


class UserProfile(models.Model):
    """ Store additional user data as we don't really want a custom user model perse """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))


class Kv15Log(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    messagecodedate = models.DateField()
    messagecodenumber = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=100)

    class Meta(object):
        verbose_name = _('Logbericht')
        verbose_name_plural = _('Logberichten')
        permissions = (
            ("view_log", _("Logberichten inzien")),
        )

    @staticmethod
    def create_log_entry(stop_message, ipaddress=None):
        log = Kv15Log()
        log.dataownercode = stop_message.dataownercode
        log.messagecodedate = stop_message.messagecodedate
        log.messagecodenumber = stop_message.messagecodenumber
        log.user = stop_message.user
        if stop_message.messagecontent is not None:  # Can happen with overrule
            log.message = stop_message.messagecontent
        else:
            log.message = ugettext("<leeg of overschrijven>")  # Default
        log.ipaddress = ipaddress
        log.save()
        return log


class MessageStatus(object):
    # Status values
    SAVED = 0
    SENT = 1
    CONFIRMED = 2
    DELETED = 5
    DELETE_SENT = 6
    DELETE_CONFIRMED = 7
    ERROR_SEND = 11
    ERROR_SEND_DELETE = 12

    STATUSES = ((SAVED, _("Opgeslagen")),  # In our database
                (SENT, _("Verstuurd")),  # Pushed to GOVI
                (CONFIRMED, _("Teruggemeld")),  # Received confirmation
                (DELETED, _("Verwijderd")),  # Received confirmation
                (DELETE_SENT, _("Verwijdering verstuurd")),  # Verwijderen succesvol
                (DELETE_CONFIRMED, _("Verwijdering teruggemeld")),  # Verwijderen teruggemeld
                (ERROR_SEND, _("Fout bij versturen")),  # Failed to push
                (ERROR_SEND_DELETE, _("Fout bij versturen verwijdering")),
                )

    @staticmethod
    def is_deleted(status):
        return status == MessageStatus.DELETED or status == MessageStatus.DELETE_SENT \
               or status == MessageStatus.DELETE_CONFIRMED or status == MessageStatus.ERROR_SEND_DELETE


class Kv15Stopmessage(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    messagecodedate = models.DateField(verbose_name=_("Datum"), default=now)
    messagecodenumber = models.IntegerField(verbose_name=_("Volgnummer"))
    messagepriority = models.CharField(max_length=10, choices=MESSAGEPRIORITY, default='PTPROCESS',
                                       verbose_name=_("Prioriteit"))
    messagetype = models.CharField(max_length=10, choices=MESSAGETYPE, default='GENERAL',
                                   verbose_name=_("Type bericht"))
    messagedurationtype = models.CharField(max_length=10, choices=MESSAGEDURATIONTYPE, default='ENDTIME',
                                           verbose_name=_("Type tijdsrooster"))
    messagestarttime = models.DateTimeField(null=True, blank=True, default=now, verbose_name=_("Begintijd"))
    messageendtime = models.DateTimeField(null=True, blank=True, default=get_end_service, verbose_name=_("Eindtijd"))
    messagecontent = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bericht")
    reasontype = models.SmallIntegerField(null=True, blank=True, choices=REASONTYPE, verbose_name=_("Type oorzaak"))
    subreasontype = models.CharField(max_length=10, blank=True, choices=SUBREASONTYPE, verbose_name=_("Oorzaak"))
    reasoncontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg oorzaak"))
    effecttype = models.SmallIntegerField(null=True, blank=True, choices=EFFECTTYPE, verbose_name=_("Type gevolg"))
    subeffecttype = models.CharField(max_length=10, blank=True, choices=SUBEFFECTTYPE, verbose_name=_("Gevolg"))
    effectcontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg gevolg"))
    measuretype = models.SmallIntegerField(null=True, blank=True, choices=MEASURETYPE,
                                           verbose_name=_("Type aanpassing"))
    submeasuretype = models.CharField(max_length=10, blank=True, choices=SUBMEASURETYPE, verbose_name=_("Aanpassing"))
    measurecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg aanpassing"))
    advicetype = models.SmallIntegerField(null=True, blank=True, choices=ADVICETYPE, verbose_name=_("Type advies"))
    subadvicetype = models.CharField(max_length=10, blank=True, choices=SUBADVICETYPE, verbose_name=_("Advies"))
    advicecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg advies"))
    messagetimestamp = models.DateTimeField(auto_now_add=True)
    isdeleted = models.BooleanField(default=False, verbose_name=_("Verwijderd?"))
    status = models.SmallIntegerField(choices=MessageStatus.STATUSES, default=0, verbose_name=_("Status"))
    stops = models.ManyToManyField(Kv1Stop, through='Kv15MessageStop')

    class Meta(object):
        verbose_name = _('KV15 Bericht')
        verbose_name_plural = _('KV15 Berichten')
        unique_together = ('dataownercode', 'messagecodedate', 'messagecodenumber',)
        permissions = (
            ("view_messages", _("Berichten bekijken")),
            ("add_messages", _("Berichten toevoegen, aanpassen of verwijderen")),
            ("view_all", _("Alle berichten inzien")),
            ("edit_all", _("Alle berichten bewerken")),
        )

    def __str__(self):
        message = self.messagecontent
        if message == "":
            message = _("<geen bericht>")
        return "%s|%s#%s : %s" % (self.dataownercode, self.messagecodedate, self.messagecodenumber, message)

    def clean(self):
        # Validate the object
        if self.messagedurationtype == 'REMOVE':
            self.messageendtime = Kv15Stopmessage.get_max_end_time()

        if self.messageendtime is not None and self.messageendtime < self.messagestarttime:
            raise ValidationError(_("Eindtijd moet na begintijd zijn"))

    def save(self, *args, **kwargs):
        # When creating or updating assign a new messagecodenumber
        # But not when it's not significant or when it's new and already set (we use this in tests)
        # New objects can be distinguished from saved ones by checking self.pk
        significant = True
        previous_pk = None
        if 'significant' in kwargs:
            significant = kwargs.pop('significant')
        if (self.messagecodenumber is None and self.pk is None) or (self.pk is not None and significant):
            self.messagecodenumber = self.get_latest_number()
        if significant:
            previous_pk = self.pk
            self.pk = None
        super(Kv15Stopmessage, self).save(*args, **kwargs)
        if previous_pk:
            prev = Kv15Stopmessage.objects.get(pk=previous_pk)
            prev.delete()  # This sets the status of the old version to deleted

    def delete(self):
        self.isdeleted = True
        self.save(significant=False)
        # Warning: Don't perform the actual delete here!

    # This method actually deletes the object - mostly we won't want this however
    def force_delete(self):
        super(Kv15Stopmessage, self).delete()

    def set_status(self, status):
        self.status = status
        self.save(significant=False)

    def to_xml(self):
        if self.stops.count() == 0:
            # Never send XML if we have no stops
            log.error("We tried to send a message with no stops. This should never happen!")
            return ""
        return render_to_string('xml/kv15stopmessage.xml', {'object': self}).replace(os.linesep, '')

    def to_xml_delete(self, messagecodenumber=None):
        """
        This is slightly weird - the logic for keeping the status in sync can't be in the model unfortunately.
        (because we can't push without stops, and stops are a submodel, requiring the main object to be saved)
        Idealy you would only allow this to be called on update (which is delete+add) or if object is deleted
        """
        return render_to_string('xml/kv15deletemessage.xml',
                                {'object': self, 'messagecodenumber': messagecodenumber}).replace(os.linesep, '')

    def is_future(self):
        return self.messagestarttime > now()

    def is_editable(self):
        return self.messageendtime > now() and self.isdeleted == False

    def is_external(self):
        return self.user_id == Kv15Stopmessage.get_external_user_id()

    def get_distinct_stop_names(self, number=15):
        """ Get a unique sample of stop names to use when we've got too many """
        return self.kv15messagestop_set.distinct('stop__name').order_by('stop__name')[0:number]

    # TODO: Move to config
    operators_with_other_systems = ["HTM", "SYNTUS"]

    def get_latest_number(self):
        """ Get the currently highest number and add one if found or start with 1  """
        num = Kv15Stopmessage.objects.filter(dataownercode=self.dataownercode,
                                             messagecodedate=self.messagecodedate).aggregate(
            models.Max('messagecodenumber'))
        if num['messagecodenumber__max'] == 9999:
            raise IntegrityError(ugettext("Teveel berichten vestuurd - probeer het morgen weer"))
        result = num['messagecodenumber__max'] + 1 if num['messagecodenumber__max'] else 1
        if self.dataownercode in self.operators_with_other_systems and result < 5000:
            result = 5000
        return result

    def get_message_duration(self):
        return (self.messageendtime.date() - self.messagestarttime.date()).days

    @staticmethod
    def get_max_end_time():
        """ Get the maximum end time, to use when we use messagedurationtype 'REMOVE' """
        return datetime(year=2099, month=12, day=31, tzinfo=get_current_timezone())

    @staticmethod
    def get_external_user_id():
        if EXTERNAL_MESSAGE_USER_ID:
            return EXTERNAL_MESSAGE_USER_ID
        else:
            # TODO: Cache this a day
            return User.objects.get(username="kv8update")


class Kv15Schedule(models.Model):
    stopmessage = models.ForeignKey(Kv15Stopmessage, on_delete=models.CASCADE)
    messagestarttime = models.DateTimeField(null=True, blank=True)
    messageendtime = models.DateTimeField(null=True, blank=True)
    weekdays = models.SmallIntegerField(null=True, blank=True)


class Kv15MessageLine(models.Model):
    stopmessage = models.ForeignKey(Kv15Stopmessage, on_delete=models.CASCADE)
    line = models.ForeignKey(Kv1Line, on_delete=models.CASCADE)

    class Meta(object):
        unique_together = ['stopmessage', 'line']


class Kv15MessageStop(models.Model):
    stopmessage = models.ForeignKey(Kv15Stopmessage, on_delete=models.CASCADE)
    stop = models.ForeignKey(Kv1Stop, related_name="messages",
                             on_delete=models.CASCADE)  # Stop to messages relation = messages

    class Meta(object):
        unique_together = ['stopmessage', 'stop']


class Kv15Scenario(models.Model):
    name = models.CharField(max_length=50, blank=True, verbose_name=_("Naam scenario"))
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    description = models.CharField(max_length=255, blank=True, verbose_name=_("Omschrijving scenario"))

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = _('Scenario')
        verbose_name_plural = _("Scenario's")
        permissions = (
            ("view_scenario", _("Scenario's bekijken")),
            ("add_scenario", _("Scenario's aanmaken")),
        )

    def plan_messages(self, user, start, end):
        saved_messages = []
        for msg in self.messages.all().order_by('updated'):
            a = Kv15Stopmessage(dataownercode=msg.dataownercode)
            a.user = user
            a.messagecodedate = now()
            a.messagestarttime = start
            a.messageendtime = end
            a.messagepriority = msg.messagepriority
            a.messagetype = msg.messagetype
            a.messagedurationtype = msg.messagedurationtype
            a.messagecontent = msg.messagecontent
            a.reasontype = msg.reasontype
            a.subreasontype = msg.subreasontype
            a.reasoncontent = msg.reasoncontent
            a.effecttype = msg.effecttype
            a.subeffecttype = msg.subeffecttype
            a.effectcontent = msg.effectcontent
            a.measuretype = msg.measuretype
            a.submeasuretype = msg.submeasuretype
            a.measurecontent = msg.measurecontent
            a.advicetype = msg.advicetype
            a.subadvicetype = msg.subadvicetype
            a.advicecontent = msg.advicecontent
            a.save()

            # Now add the stops
            for msg_stop in msg.stops.all():
                Kv15MessageStop(stopmessage=a, stop=msg_stop.stop).save()

            Kv15ScenarioInstance(scenario=self, message=a).save()
            saved_messages.append(a)

        return saved_messages

    def delete_all(self):
        msgs = []
        for inst in Kv15ScenarioInstance.objects.filter(scenario=self, message__messageendtime__gt=now):
            inst.message.delete()
            msgs.append(inst.message.to_xml_delete())

        return msgs


class Kv15ScenarioMessage(models.Model):
    """ This stores a 'template' to be used for easily constructing normal KV15 messages """
    scenario = models.ForeignKey(Kv15Scenario, related_name='messages', on_delete=models.CASCADE)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    messagepriority = models.CharField(max_length=10, choices=MESSAGEPRIORITY, default='PTPROCESS',
                                       verbose_name=_("Prioriteit"))
    messagetype = models.CharField(max_length=10, choices=MESSAGETYPE, default='GENERAL',
                                   verbose_name=_("Type bericht"))
    messagedurationtype = models.CharField(max_length=10, choices=MESSAGEDURATIONTYPE, default='ENDTIME',
                                           verbose_name=_("Type tijdsrooster"))
    messagecontent = models.CharField(max_length=255, blank=True, verbose_name="Bericht")
    reasontype = models.SmallIntegerField(null=True, blank=True, choices=REASONTYPE, verbose_name=_("Type oorzaak"))
    subreasontype = models.CharField(max_length=10, blank=True, choices=SUBREASONTYPE, verbose_name=_("Oorzaak"))
    reasoncontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg oorzaak"))
    effecttype = models.SmallIntegerField(null=True, blank=True, choices=EFFECTTYPE, verbose_name=_("Type gevolg"))
    subeffecttype = models.CharField(max_length=10, blank=True, choices=SUBEFFECTTYPE, verbose_name=_("Gevolg"))
    effectcontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg gevolg"))
    measuretype = models.SmallIntegerField(null=True, blank=True, choices=MEASURETYPE,
                                           verbose_name=_("Type aanpassing"))
    submeasuretype = models.CharField(max_length=10, blank=True, choices=SUBMEASURETYPE, verbose_name=_("Aanpassing"))
    measurecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg aanpassing"))
    advicetype = models.SmallIntegerField(null=True, blank=True, choices=ADVICETYPE, verbose_name=_("Type advies"))
    subadvicetype = models.CharField(max_length=10, blank=True, choices=SUBADVICETYPE, verbose_name=_("Advies"))
    advicecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg advies"))
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        message = self.messagecontent
        if message == "":
            message = _("<geen bericht>")
        return "%s : %s" % (self.scenario.name, message)

    def get_distinct_stop_names(self, number=15):
        """ Get a unique sample of stop names to use when we've got too many """
        return self.stops.distinct('stop__name').order_by('stop__name')[0:number]

    class Meta(object):
        verbose_name = _('Scenario bericht')
        verbose_name_plural = _("Scenario berichten")


class Kv15ScenarioStop(models.Model):
    """ For the template, this links a stop """
    message = models.ForeignKey(Kv15ScenarioMessage, related_name='stops', on_delete=models.CASCADE)
    stop = models.ForeignKey(Kv1Stop, related_name="scenario_stop",  on_delete=models.CASCADE)


class Kv15ScenarioInstance(models.Model):
    """ This keeps track of instances of scenarios to be able to easily clean them up """
    scenario = models.ForeignKey(Kv15Scenario, on_delete=models.CASCADE)
    message = models.ForeignKey(Kv15Stopmessage, on_delete=models.CASCADE)


class Kv17Change(models.Model):
    """
    Container for a kv17 change for a particular journey
    """
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    operatingday = models.DateField(verbose_name=_("Datum"))
    line = models.ForeignKey(Kv1Line, verbose_name=_("Lijn"), on_delete=models.CASCADE)
    journey = models.ForeignKey(Kv1Journey, verbose_name=_("Rit"), related_name="changes",
                                on_delete=models.CASCADE)  # "A journey has changes"
    reinforcement = models.IntegerField(default=0, verbose_name=_("Versterkingsnummer"))  # Never fill this for now
    is_cancel = models.BooleanField(default=True, verbose_name=_("Opgeheven?"),
                                    help_text=_("Rit kan ook een toelichting zijn voor een halte"))
    is_recovered = models.BooleanField(default=False, verbose_name=_("Teruggedraaid?"))
    created = models.DateTimeField(auto_now_add=True)
    recovered = models.DateTimeField(null=True, blank=True)  # Not filled till recovered

    def delete(self):
        self.is_recovered = True
        self.recovered = now()
        self.save()
        # Warning: Don't perform the actual delete here!

    def force_delete(self):
        super(Kv17Change, self).delete()

    def to_xml(self):
        """
        This xml will reflect the status of the object - wheter we've been canceled or recovered
        """
        return render_to_string('xml/kv17journey.xml', {'object': self}).replace(os.linesep, '')

    class Meta(object):
        verbose_name = _('Ritaanpassing')
        verbose_name_plural = _("Ritaanpassingen")
        unique_together = ('operatingday', 'line', 'journey', 'reinforcement')
        permissions = (
            ("view_change", _("Ritaanpassingen bekijken")),
            ("add_change", _("Ritaanpassingen aanmaken")),
        )

    def __str__(self):
        return "%s Lijn %s Rit# %s" % (self.operatingday, self.line, self.journey.journeynumber)

    def realtime_id(self):
        return "%s:%s:%s" % (self.dataownercode, self.line.lineplanningnumber, self.journey.journeynumber)


class Kv17JourneyChange(models.Model):
    """
    Store cancel and recover for a complete trip
    If is_recovered = False is a cancel, else it's no longer
    """
    change = models.ForeignKey(Kv17Change, related_name="journey_details", on_delete=models.CASCADE)
    reasontype = models.SmallIntegerField(null=True, blank=True, choices=REASONTYPE, verbose_name=_("Type oorzaak"))
    subreasontype = models.CharField(max_length=10, blank=True, choices=SUBREASONTYPE, verbose_name=_("Oorzaak"))
    reasoncontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg oorzaak"))
    advicetype = models.SmallIntegerField(null=True, blank=True, choices=ADVICETYPE, verbose_name=_("Type advies"))
    subadvicetype = models.CharField(max_length=10, blank=True, choices=SUBADVICETYPE, verbose_name=_("Advies"))
    advicecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg advies"))

    class Meta(object):
        verbose_name = _('Ritaanpassingsdetails')
        verbose_name_plural = _("Ritaanpassingendetails")

    def __str__(self):
        return "%s Details" % self.change


class Kv17StopChange(models.Model):
    """
    Store one of the five change types for an individual stop
    """
    STOP_CHANGE_TYPES = ((1, "SHORTEN"),
                         (2, "LAG"),
                         (3, "CHANGEPASSTIMES"),
                         (4, "CHANGEDESTINATION"),
                         (5, "MUTATIONMESSAGE")
                         )

    change = models.ForeignKey(Kv17Change, related_name="stop_change", on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(null=False, choices=STOP_CHANGE_TYPES)
    # All messages
    stop = models.ForeignKey(Kv1Stop, on_delete=models.CASCADE)
    stoporder = models.IntegerField(null=False)  # This is duplicate/can be easily derived
    # Lag
    lag = models.IntegerField(null=True, blank=True)  # In seconds
    # ChangePassTimes
    targetarrival = models.DateTimeField(null=True, blank=True)
    targetdeparture = models.DateTimeField(null=True, blank=True)
    stoptype = models.CharField(choices=STOPTYPES, default="INTERMEDIATE", max_length=12, null=True, blank=True)
    # ChangeDestination
    destinationcode = models.CharField(max_length=10, blank=True)
    destinationname50 = models.CharField(max_length=50, blank=True)
    destinationname16 = models.CharField(max_length=16, blank=True)
    destinationdetail16 = models.CharField(max_length=16, blank=True)
    destinationdisplay16 = models.CharField(max_length=16, blank=True)
    # MutationMessage
    reasontype = models.SmallIntegerField(null=True, blank=True, choices=REASONTYPE, verbose_name=_("Type oorzaak"))
    subreasontype = models.CharField(max_length=10, blank=True, choices=SUBREASONTYPE, verbose_name=_("Oorzaak"))
    reasoncontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg oorzaak"))
    advicetype = models.SmallIntegerField(null=True, blank=True, choices=ADVICETYPE, verbose_name=_("Type advies"))
    subadvicetype = models.CharField(max_length=10, blank=True, choices=SUBADVICETYPE, verbose_name=_("Advies"))
    advicecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg advies"))

    class Meta(object):
        verbose_name = _('Halteaanpassing')
        verbose_name_plural = _("Halteaanpassingen")


class Kv1StopFilter(models.Model):
    name = models.CharField(_("Naam"), max_length=25)
    description = models.TextField(max_length=200, blank=True, null=True)
    enabled = models.BooleanField(default=True)

    class Meta(object):
        verbose_name = _('Filter')
        verbose_name_plural = _("Filters")
        permissions = (
            ("edit_filters", _("Filters bewerken")),
        )

    def __str__(self):
        return self.name

    @staticmethod
    def get_filters():
        return Kv1StopFilter.objects.filter(enabled=True).values_list('id', 'name')


class Kv1StopFilterStop(models.Model):
    filter = models.ForeignKey(Kv1StopFilter, related_name="stops", on_delete=models.CASCADE)
    stop = models.ForeignKey(Kv1Stop, on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _('Filter halte')
        verbose_name_plural = _("Filter haltes")
        unique_together = ('filter', 'stop')
        ordering = ['stop__name', 'stop__timingpointcode']
