import logging
from django.utils.timezone import now
from django.conf import settings
from httplib import HTTPConnection
import pytz

class Push:
    def __init__(self, subscriberid = 'openOV', dossiername = None, content = None, namespace = None):
        self.log = logging.getLogger(__name__)
        self.subscriberid = subscriberid
        self.timestamp = now(pytz.timezone('Europe/Amsterdam'))

        self.dossiername = dossiername
        self.content = content
        self.namespace = namespace

    def __str__(self):
        data = {'namespace': self.namespace,
                'subscriberid': self.subscriberid,
                'dossiername': self.dossiername,
                'timestamp':self.timestamp.isoformat('T'), #Iso without microseconds
                'content': str(self.content) }

        xml = """<VV_TM_PUSH xmlns="%(namespace)s">
<SubscriberID>%(subscriberid)s</SubscriberID>
<Version>BISON 8.1.0.0</Version>
<DossierName>%(dossiername)s</DossierName>
<Timestamp>%(timestamp)s</Timestamp>
%(content)s
</VV_TM_PUSH>""" % data

        return xml

    def push(self, remote, path):
        content = str(self)
        if settings.GOVI_PUSH_DEBUG:
            self.log.debug(content)

        response_code = -1
        response_content = None
        if settings.GOVI_PUSH_SEND:
            conn = HTTPConnection(remote)
            conn.request("POST", path, content, {"Content-type": "application/xml"})
            response = conn.getresponse()
            response_code = response.status
            response_content = response.read()
            conn.close()
            if settings.GOVI_PUSH_DEBUG:
                self.log.debug(response_content)

        return (response_code,response_content)
