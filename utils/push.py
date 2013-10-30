from django.utils.timezone import now
from django.conf import settings
from httplib import HTTPConnection
import pytz

class Push:
    def __init__(self, subscriberid = 'openOV', dossiername = None, content = None, namespace = None):
        self.subscriberid = subscriberid
        self.timestamp = now

        self.dossiername = dossiername
        self.content = content
        self.namespace = namespace

    def __str__(self):
        data = {'namespace': self.namespace,
                'subscriberid': self.subscriberid,
                'dossiername': self.dossiername,
                'timestamp':self.timestamp.isoformat(),
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
        response = None
        content = str(self)
        if settings.DEBUG:
            print content
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
                print response_content

        #if store and response is not None and 'ResponseCode>OK<' in response:
        #    self.content.save()

        return (response_code,response_content)