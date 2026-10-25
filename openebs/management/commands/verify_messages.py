# Hack to disable logging for now
from datetime import datetime
from django.db import connection
from kv1.models import Kv1Stop

connection.use_debug_cursor = False

import logging
from io import BytesIO
from gzip import GzipFile
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
import zmq
from openebs.models import Kv15Stopmessage, MessageStatus, Kv15MessageStop
from openebs.views_push import Kv15PushMixin
from utils.views import ExternalMessagePushMixin


class Command(BaseCommand):
    log = logging.getLogger('openebs.kv8verify')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.siri_sx_pushers = []
        self.imported = {}  # Messages to push as SIRI-SX once the whole packet is in, by pk
        self.user = None

    def handle(self, *args, **options):
        if settings.GOVI_VERIFY_SIRI_SX:
            self.siri_sx_pushers = self.get_siri_sx_pushers()
            print("Pushing imported messages as SIRI-SX to: %s" % ", ".join(p.alias for p in self.siri_sx_pushers))
        print('Setting up a ZeroMQ SUB: %s\n' % (settings.GOVI_VERIFY_FEED))
        sub = Command.setup_subscription()
        print("Started at %s, further messages are in your logfile" % (datetime.now().isoformat('T')))
        while True:
            self.receive_message(sub)

    def receive_message(self, sub):
        multipart = sub.recv_multipart()
        try:
            contents = b''.join(multipart[1:])
            contents = GzipFile('','r',0,BytesIO(contents)).read()
            contents = contents.decode('UTF-8')
        except:
            contents = b''.join(multipart[1:])
            contents = contents.decode('UTF-8')
        try:
            self.parse_message(contents)
        except:
            print(contents)
            raise
        self.push_imported()

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
                for k, v in zip(keys, values):
                    if v == '\\0':
                        row[k] = None
                    else:
                        row[k] = v
                # self.log.debug("Got new message of type %s" % type)
                if type == 'GENERALMESSAGEUPDATE':
                    self.process_message(row, False)
                elif type == 'GENERALMESSAGEDELETE':
                    self.process_message(row, True)
                else:
                    self.log.warning("Don't have a handler for messages of type %s" % type)

    @transaction.atomic
    def process_message(self, row, deleted):
        if not deleted:
            msg, created = Kv15Stopmessage.objects.get_or_create(dataownercode=row['DataOwnerCode'],
                                                                 messagecodedate=row['OriginalMessageCodeDate'],
                                                                 messagecodenumber=row['OriginalMessageCodeNumber'],
                                                                 defaults={'user': self.get_user()})
     

            msg.status = MessageStatus.CONFIRMED
            # In case this is an update, set these fields to properly restore our message:
            msg.kv8messagecodedate = row['MessageCodeDate']
            msg.kv8messagecodenumber = row['MessageCodeNumber']
            msg.messagestarttime = row['MessageStartTime']
            msg.messageendtime = row['MessageEndTime']
            msg.isdeleted = False
            if created:
                self.log.info("Message added and confirmed: %s (Stop: %s)" % (msg, row['TimingPointCode']))
                self.copy_message_content(msg, row)
            else:
                self.log.info("Message confirmed: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))

            msg.save(significant=False)

            # Handle stop
            self.add_stop_for_message(msg, row)
            self.remember_imported(msg)

        else:
            msg, created = Kv15Stopmessage.objects.get_or_create(dataownercode=row['DataOwnerCode'],
                                                                 kv8messagecodedate=row['MessageCodeDate'],
                                                                 kv8messagecodenumber=row['MessageCodeNumber'],
                                                                 defaults={'user': self.get_user()})

            if not created:
                self.log.info("Message confirmed deleted: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))
            else:
                self.log.info("Message added and confirmed deleted: %s (Stop/TPC %s)" % (msg, row['TimingPointCode']))
            
            msg.kv8messagecodedate = row['MessageCodeDate']
            msg.kv8messagecodenumber = row['MessageCodeNumber']
            msg.status = MessageStatus.DELETE_CONFIRMED
            msg.messageendtime = now()
            msg.isdeleted = True
   
            msg.save(significant=False)

            # Handle stop
            self.add_stop_for_message(msg, row)
            if not created:  # Nothing to close if we never had it
                self.remember_imported(msg)

    def remember_imported(self, msg):
        """ Our own messages were already pushed as SIRI-SX when they were made in OpenEBS """
        if len(self.siri_sx_pushers) > 0 and msg.user_id == self.get_kv8_user().pk:
            self.imported[msg.pk] = msg

    def push_imported(self):
        """
        Push the messages imported from this packet as SIRI-SX. A message has a row per stop, so it's pushed once with
        all the stops of the packet, not once per row
        """
        for msg in self.imported.values():
            if msg.isdeleted:
                content = msg.to_xml_delete()
            elif msg.stops.count() > 0:
                content = msg.to_xml()
            else:
                self.log.warning("Not pushing %s as SIRI-SX, none of its stops are known" % msg)
                continue
            for pusher in self.siri_sx_pushers:
                if ExternalMessagePushMixin.push_siri_sx(pusher, content):
                    self.log.info("Pushed %s as SIRI-SX to %s" % (msg, pusher.alias))
        self.imported = {}

    @staticmethod
    def get_siri_sx_pushers():
        """ The SIRI-SX endpoints of the KV15 destinations. We don't push the KV15 itself, it came from GOVI """
        return [pusher.siri_sx for pusher in Kv15PushMixin().pushers if pusher.siri_sx is not None]

    def get_kv8_user(self):
        if self.user is None:
            self.user = self.get_user()
        return self.user

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
        if row['QuayCode'] is None or len(row['QuayCode']) == 0:
            return

        stops = Kv1Stop.objects.filter(quaycoderef=row['QuayCode'])
        for stop in stops:
            message_stop, created = Kv15MessageStop.objects.get_or_create(stopmessage=msg, stop=stop)
            if created:
                self.log.debug("Stop added to message: %s|%s#%s (Stop/TPC %s)" % (
                msg.dataownercode, msg.messagecodedate, msg.messagecodenumber, row['TimingPointCode']))
                message_stop.save()
        if len(stops) == 0:
            self.log.error("Tried to add stops to message but couldn't find matching TPC: %s|%s#%s (Stop/TPC %s)" % (
            msg.dataownercode, msg.messagecodedate, msg.messagecodenumber, row['TimingPointCode']))

    @staticmethod
    def setup_subscription():
        context = zmq.Context()
        sub = context.socket(zmq.SUB)
        sub.connect(settings.GOVI_VERIFY_FEED)
        sub.setsockopt_string(zmq.SUBSCRIBE, settings.GOVI_VERIFY_SUB)
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
