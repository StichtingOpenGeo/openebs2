# Hack to disable logging for now
from django.db import connection
connection.use_debug_cursor = False

import logging
from StringIO import StringIO
from gzip import GzipFile
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
import zmq
from openebs.models import Kv15Stopmessage, MessageStatus

class Command(BaseCommand):
    log = logging.getLogger('openebs.kv8verify')

    def handle(self, *args, **options):
        print 'Setting up a ZeroMQ SUB: %s\n' % (settings.GOVI_VERIFY_FEED)
        context = zmq.Context()
        sub = context.socket(zmq.SUB)
        sub.connect(settings.GOVI_VERIFY_FEED)
        sub.setsockopt(zmq.SUBSCRIBE, settings.GOVI_VERIFY_SUB)
        print "Further messages are in your logfile"
        while True:
            multipart = sub.recv_multipart()
            try:
                content = GzipFile('','r',0,StringIO(''.join(multipart[1:]))).read()
            except:
                content = ''.join(multipart[1:])
            self.recvPackage(content)

    def recvPackage(self, content):
        for line in content.split('\r\n')[:-1]:
            if line[0] == '\\':
                    # control characters
                if line[1] == 'G':
                    label, name, subscription, path, endian, enc, res1, timestamp, _ = line[2:].split('|')
                elif line[1] == 'T':
                    type = line[2:].split('|')[1]
                elif line[1] == 'L':
                    keys = line[2:].split('|')
            else:
                row = {}
                values = line.split('|')
                for k,v in map(None, keys, values):
                    if v == '\\0':
                        row[k] = None
                    else:
                        row[k] = v
                self.log.debug("Got new message of type %s" % type)
                if type == 'GENERALMESSAGEUPDATE':
                    self.processMessage(row)
                elif type == 'GENERALMESSAGEDELETE':
                    self.processDelMessage(row)
                else:
                    self.log.warning("Don't have a handler for messages of type %s" % type)

    @transaction.commit_on_success
    def processMessage(self, row):

        msg, created = Kv15Stopmessage.objects.get_or_create(dataownercode=row['DataOwnerCode'], messagecodedate=row['MessageCodeDate'],
                                       messagecodenumber=row['MessageCodeNumber'], defaults={ 'user' : self.get_user()})
        self.log.info("Setting status confirmed for adding of message: %s (Stop: %s)" % (msg, row['TimingPointCode']))
        msg.status = MessageStatus.CONFIRMED
        # In case this is an update, set these fields to properly restore our message:
        msg.messagestarttime = row['MessageStartTime']
        msg.messageendtime = row['MessageEndTime']
        msg.isdeleted = False
        if created:
            self.log.info("Creating new message which wasn't in DB (note, stops will be blank): %s" % msg)
            msg.messagecontent = row['MessageContent']
            msg.messagetimestamp = row['MessageTimeStamp']
            msg.messagetype = row['MessageType']
            msg.messagedurationtype = row['MessageDurationType']
            self.set_if_filled(msg, 'reasontype', row['ReasonType'])
            self.set_if_filled(msg, 'subreasontype', row['SubReasonType'])
            self.set_if_filled(msg, 'reasoncontent', row['ReasonContent'])
            self.set_if_filled(msg, 'effecttype', row['EffectType'])
            self.set_if_filled(msg, 'subeffecttype', row['SubEffectType'])
            self.set_if_filled(msg, 'effectcontent', row['EffectContent'])
            self.set_if_filled(msg, 'measuretype', row['MeasureType'])
            self.set_if_filled(msg, 'submeasuretype', row['SubMeasureType'])
            self.set_if_filled(msg, 'measurecontent', row['MeasureContent'])
            self.set_if_filled(msg, 'advicetype', row['AdviceType'])
            self.set_if_filled(msg, 'subadvicetype', row['SubAdviceType'])
            self.set_if_filled(msg, 'advicecontent', row['AdviceContent'])
        msg.save()

        # TODO Handle stops here

    @transaction.commit_on_success
    def processDelMessage(self, row):
        try:
            msg = Kv15Stopmessage.objects.get(dataownercode=row['DataOwnerCode'], messagecodedate=row['MessageCodeDate'],
                                       messagecodenumber=row['MessageCodeNumber'])
            msg.status = MessageStatus.DELETE_CONFIRMED
            msg.isdeleted = True
            msg.messageendtime = now()
            msg.save()
            self.log.error("Confirmed deletion of message: %s (Stop %s)" % (msg, row['TimingPointCode']))
            # TODO Handle stops here
        except Kv15Stopmessage.DoesNotExist:
            self.log.error("Tried to delete message that doesn't exist: %s" % row)

    def get_user(self):
        return User.objects.get_or_create(username="kv8update")[0]

    def check_filled(self, val):
        return True if val is not None or val != '' else False

    def set_if_filled(self, instance, field, value):
        if value is not None and value != '':
            setattr(instance, field, value)
