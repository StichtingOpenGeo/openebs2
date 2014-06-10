from datetime import date
from StringIO import StringIO
from gzip import GzipFile
import zmq

from django.core.management import BaseCommand
from django.contrib.gis.geos import Point
from django.conf import settings

# Hack to disable logging for now
from django.db import connection
connection.use_debug_cursor = False

import logging
from reports.json6 import kv6tojson
from reports.models import Kv6Log
from utils.geo import transform_rd


class Command(BaseCommand):
    log = logging.getLogger('openebs.kv6log')

    filter_dataowner = ('HTM')

    def handle(self, *args, **options):
        print 'Setting up a ZeroMQ SUB: %s\n' % settings.KV6_FEED
        context = zmq.Context()
        sub = context.socket(zmq.SUB)
        sub.connect(settings.KV6_FEED)
        sub.setsockopt(zmq.SUBSCRIBE, "/RIG")
        while True:
            multipart = sub.recv_multipart()
            try:
                content = GzipFile('','r',0,StringIO(''.join(multipart[1:]))).read()
            except:
                content = ''.join(multipart[1:])
            message = kv6tojson(content)
            for vehicle in message:
                if vehicle['dataownercode'] in self.filter_dataowner and vehicle['lineplanningnumber'] is not None:
                    self.save_log(vehicle)
            del multipart, content, message

    def save_log(self, vehicle):
        split_date = vehicle['operatingday'].split('-')
        default = 0
        if 'punctuality' in vehicle:
            default = int(vehicle['punctuality'])
        logline, created = Kv6Log.objects.get_or_create(dataownercode = vehicle['dataownercode'],
                                               lineplanningnumber=vehicle['lineplanningnumber'],
                                               journeynumber = int(vehicle['journeynumber']),
                                               operatingday=date(int(split_date[0]), int(split_date[1]), int(split_date[2])),
                                               defaults={'last_punctuality': default, 'max_punctuality': default, 'vehiclenumber' : vehicle['vehiclenumber']})
        if 'punctuality' in vehicle:
            logline.last_punctuality = int(vehicle['punctuality'])
            if logline.max_punctuality < logline.last_punctuality:
                logline.max_punctuality = logline.last_punctuality
        if 'rd_x' in vehicle and vehicle['rd_x'] is not None:
            point = transform_rd(Point(vehicle['rd_x'], vehicle['rd_y'], srid=28992))
            logline.last_position = point.wkt
        logline.save()
