# Hack to disable logging for now
from django.db import connection
from kv1.models import Kv1Stop

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
from openebs.models import Kv15Stopmessage, MessageStatus, Kv15MessageStop


class Command(BaseCommand):
    log = logging.getLogger('openebs.kv8verify')


    def handle(self, *args, **options):
        print 'Setting up a ZeroMQ SUB: %s\n' % (settings.GOVI_VERIFY_FEED)
        sub = Command.setup_subscription()
        print "Further messages are in your logfile"
        while True:
            self.receive_message(sub)

    def receive_message(self, sub):
        multipart = sub.recv_multipart()
        try:
            content = GzipFile('', 'r', 0, StringIO(''.join(multipart[1:]))).read()
        except:
            content = ''.join(multipart[1:])
        self.parse_message(content)

    def parse_message(self, content):
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
                for k, v in map(None, keys, values):
                    if v == '\\0':
                        row[k] = None
                    else:
                        row[k] = v
                #self.log.debug("Got new message of type %s" % type)
                if type == 'GENERALMESSAGEUPDATE':
                    self.process_message(row, False)
                elif type == 'GENERALMESSAGEDELETE':
                    self.process_message(row, True)
                else:
                    self.log.warning("Don't have a handler for messages of type %s" % type)

    @transaction.commit_on_success
    def process_message(self, row, deleted):
        msg, created = Kv15Stopmessage.objects.get_or_create(dataownercode=row['DataOwnerCode'],
                                                             messagecodedate=row['MessageCodeDate'],
                                                             messagecodenumber=row['MessageCodeNumber'],
                                                             defaults={'user': self.get_user()})
        if not deleted:
            msg.status = MessageStatus.CONFIRMED
            # In case this is an update, set these fields to properly restore our message:
            msg.messagestarttime = row['MessageStartTime']
            msg.messageendtime = row['MessageEndTime']
            msg.isdeleted = False
            if created:
                self.log.info("Message added and confirmed: %s (Stop: %s)" % (msg, row['TimingPointCode']))
                self.copy_message_content(msg, row)
            else:
                self.log.info("Message confirmed: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))
        else:
            if not created:
                self.log.error("Message confirmed deleted: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))
            else:
                self.log.error("Message added and confirmed deleted: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))
            msg.status = MessageStatus.DELETE_CONFIRMED
            msg.messageendtime = now()
            msg.isdeleted = True

        msg.save()

        # Handle stop
        self.add_stop_for_message(msg, row)

    def copy_message_content(self, msg, row):
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

    def add_stop_for_message(self, msg, row):
        stops = Kv1Stop.objects.filter(timingpointcode=row['TimingPointCode'])
        for stop in stops:
            message_stop, created = Kv15MessageStop.objects.get_or_create(stopmessage=msg, stop=stop)
            if created:
                self.log.debug("Stop added to message: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))
                message_stop.save()
        if len(stops) == 0:
            self.log.error("Tried to add stops to message but couldn't find matching TPC: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))

    @staticmethod
    def setup_subscription():
        context = zmq.Context()
        sub = context.socket(zmq.SUB)
        sub.connect(settings.GOVI_VERIFY_FEED)
        sub.setsockopt(zmq.SUBSCRIBE, settings.GOVI_VERIFY_SUB)
        return sub


    @staticmethod
    def get_user():
        return User.objects.get_or_create(username="kv8update")[0]

    @staticmethod
    def check_filled(val):
        return True if val is not None or val != '' else False

    @staticmethod
    def set_if_filled(instance, field, value):
        if value is not None and value != '':
            setattr(instance, field, value)
