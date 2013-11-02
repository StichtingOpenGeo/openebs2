# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.timezone import now
from kv1.models import Kv1Stop, Kv1Line

from kv15.enum import *

class UserProfile(models.Model):
    ''' Store additional user data as we don't really want a custom user model perse '''
    user = models.OneToOneField(User)
    company = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))

class Kv15Log(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    messagecodedate = models.DateField()
    messagecodenumber = models.DecimalField(max_digits=4, decimal_places=0)
    user = models.ForeignKey(User)
    message = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('Logbericht')
        verbose_name_plural = _('Logberichten')
        permissions = (
            ("view_log", _("Logberichten inzien")),
        )

    @staticmethod
    def create_log_entry(stop_message, ipaddress = None):
        log = Kv15Log()
        log.dataownercode = stop_message.dataownercode
        log.messagecodedate = stop_message.messagecodedate
        log.messagecodenumber = stop_message.messagecodenumber
        log.user = stop_message.user
        log.message = stop_message.messagecontent
        log.ipaddress = ipaddress
        log.save()
        return log


class Kv15Stopmessage(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    messagecodedate = models.DateField(verbose_name=_("Datum"))
    messagecodenumber = models.DecimalField(max_digits=4, decimal_places=0, verbose_name=_("Volgnummer"))
    messagepriority = models.CharField(max_length=10, choices=MESSAGEPRIORITY, default='PTPROCESS', verbose_name=_("Prioriteit"))
    messagetype = models.CharField(max_length=10, choices=MESSAGETYPE, default='GENERAL', verbose_name=_("Type bericht"))
    messagedurationtype = models.CharField(max_length=10, choices=MESSAGEDURATIONTYPE, default='ENDTIME', verbose_name=_("Type tijdsrooster"))
    messagestarttime = models.DateTimeField(null=True, blank=True, default=now, verbose_name=_("Begintijd"))
    messageendtime = models.DateTimeField(null=True, blank=True, verbose_name=_("Eindtijd"))
    messagecontent = models.CharField(max_length=255, blank=True, verbose_name="Bericht")
    reasontype = models.SmallIntegerField(null=True, blank=True, choices=REASONTYPE, verbose_name=_("Type oorzaak"))
    subreasontype = models.CharField(max_length=10, blank=True, choices=SUBREASONTYPE, verbose_name=_("Oorzaak"))
    reasoncontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg oorzaak"))
    effecttype = models.SmallIntegerField(null=True, blank=True, choices=EFFECTTYPE,  verbose_name=_("Type gevolg"))
    subeffecttype = models.CharField(max_length=10, blank=True, choices=SUBEFFECTTYPE, verbose_name=_("Gevolg"))
    effectcontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg gevolg"))
    measuretype = models.SmallIntegerField(null=True, blank=True, choices=MEASURETYPE, verbose_name=_("Type aanpassing"))
    submeasuretype = models.CharField(max_length=10, blank=True, choices=SUBMEASURETYPE, verbose_name=_("Aanpassing"))
    measurecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg aanpassing"))
    advicetype = models.SmallIntegerField(null=True, blank=True, choices=ADVICETYPE, verbose_name=_("Type advies"))
    subadvicetype = models.CharField(max_length=10, blank=True, choices=SUBADVICETYPE, verbose_name=_("Advies"))
    advicecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg advies"))
    messagetimestamp = models.DateTimeField(auto_now_add=True)
    isdeleted = models.BooleanField(default=False, verbose_name=_("Verwijderd?"))

    class Meta:
        verbose_name = _('KV15 Bericht')
        verbose_name_plural = _('KV15 Berichten')
        unique_together = ('dataownercode', 'messagecodedate', 'messagecodenumber',)
        permissions = (
            ("view_messages", _("Berichten bekijken")),
            ("add_messages", _("Berichten toevoegen, aanpassen of verwijderen")),
        )

    def __unicode__(self):
        message = self.messagecontent
        if message == "":
            message = _("<geen bericht>")
        return "%s#%s : %s" % (self.messagecodedate, self.messagecodenumber, message)

    def clean(self):
        # Validate the object
        if self.messageendtime is not None and self.messageendtime < self.messagestarttime:
            raise ValidationError(_("Eindtijd moet na begintijd zijn"))

    def save(self, *args, **kwargs):
        # Set the messagecodenumber to the latest highest number for new messages
        self.messagecodenumber = self.get_latest_number()
        super(Kv15Stopmessage, self).save(*args, **kwargs)

    def delete(self):
        self.isdeleted = True
        self.save()
        # Warning: Don't perform the actual delete here!

    # This method actually deletes the object - mostly we won't want this however
    def force_delete(self):
        super(Kv15Stopmessage, self).delete()

    def is_future(self):
        return self.messagestarttime > now()

    def get_latest_number(self):
        '''Get the currently highest number and add one if found or start with 1  '''
        num = Kv15Stopmessage.objects.filter(dataownercode=self.dataownercode, messagecodedate=self.messagecodedate).aggregate(models.Max('messagecodenumber'))
        if num['messagecodenumber__max'] == 9999:
            raise IntegrityError(ugettext("Teveel berichten vestuurd - probeer het morgen weer"))
        return num['messagecodenumber__max'] + 1 if num['messagecodenumber__max'] else 1

class Kv15Schedule(models.Model):
    stopmessage = models.ForeignKey(Kv15Stopmessage)
    messagestarttime = models.DateTimeField(null=True, blank=True)
    messageendtime = models.DateTimeField(null=True, blank=True)
    weekdays = models.SmallIntegerField(null=True, blank=True)

class Kv15MessageLine(models.Model):
    stopmessage = models.ForeignKey(Kv15Stopmessage)
    line = models.ForeignKey(Kv1Line)

class Kv15MessageStop(models.Model):
    stopmessage = models.ForeignKey(Kv15Stopmessage)
    stop = models.ForeignKey(Kv1Stop, related_name="messages") # Stop to messages relation = messages

class Kv15Scenario(models.Model):
    name = models.CharField(max_length=50, blank=True, verbose_name=_("Naam scenario"))
    description = models.CharField(max_length=255, blank=True, verbose_name=_("Omschrijving scenario"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Scenario')
        verbose_name_plural = _("Scenario's")
        permissions = (
            ("view_scenario", _("Scenario's bekijken")),
            ("add_scenario", _("Scenario's aanmaken")),
        )

class Kv15ScenarioMessage(models.Model):
    """ This stores a 'template' to be used for easily constructing normal KV15 messages """
    scenario = models.ForeignKey(Kv15Scenario)
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE, verbose_name=_("Vervoerder"))
    messagepriority = models.CharField(max_length=10, choices=MESSAGEPRIORITY, default='PTPROCESS', verbose_name=_("Prioriteit"))
    messagetype = models.CharField(max_length=10, choices=MESSAGETYPE, default='GENERAL', verbose_name=_("Type bericht"))
    messagedurationtype = models.CharField(max_length=10, choices=MESSAGEDURATIONTYPE, default='ENDTIME', verbose_name=_("Type tijdsrooster"))
    messagecontent = models.CharField(max_length=255, blank=True, verbose_name="Bericht")
    reasontype = models.SmallIntegerField(null=True, blank=True, choices=REASONTYPE, verbose_name=_("Type oorzaak"))
    subreasontype = models.CharField(max_length=10, blank=True, choices=SUBREASONTYPE, verbose_name=_("Oorzaak"))
    reasoncontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg oorzaak"))
    effecttype = models.SmallIntegerField(null=True, blank=True, choices=EFFECTTYPE, verbose_name=_("Type gevolg"))
    subeffecttype = models.CharField(max_length=10, blank=True, choices=SUBEFFECTTYPE, verbose_name=_("Gevolg"))
    effectcontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg gevolg"))
    measuretype = models.SmallIntegerField(null=True, blank=True, choices=MEASURETYPE, verbose_name=_("Type aanpassing"))
    submeasuretype = models.CharField(max_length=10, blank=True, choices=SUBMEASURETYPE, verbose_name=_("Aanpassing"))
    measurecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg aanpassing"))
    advicetype = models.SmallIntegerField(null=True, blank=True, choices=ADVICETYPE, verbose_name=_("Type advies"))
    subadvicetype = models.CharField(max_length=10, blank=True, choices=SUBADVICETYPE, verbose_name=_("Advies"))
    advicecontent = models.CharField(max_length=255, blank=True, verbose_name=_("Uitleg advies"))
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        message = self.messagecontent
        if message == "":
            message = _("<geen bericht>")
        return "%s : %s" % (self.scenario.name, message)

    class Meta:
        verbose_name = _('Scenario bericht')
        verbose_name_plural = _("Scenario berichten")

class Kv15ScenarioStop(models.Model):
    """ For the template, this links a stop """
    message = models.ForeignKey(Kv15ScenarioMessage)
    stop = models.ForeignKey(Kv1Stop)