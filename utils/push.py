import logging, socket
from django.utils.timezone import now
from django.conf import settings
import httplib

class Push:
    def __init__(self, subscriberid = 'openOV', namespace = None):
        self.log = logging.getLogger("openebs.push")
        self.subscriberid = subscriberid
        self.timestamp = now()

        self.namespace = namespace

    def __str__(self):
        data = {'namespace': self.namespace,
                'subscriberid': self.subscriberid,
                'dossiername': self.dossiername,
                'timestamp':self.timestamp.isoformat('T'),
                'content': str(self.content) }

        xml = """<VV_TM_PUSH xmlns="%(namespace)s">
<SubscriberID>%(subscriberid)s</SubscriberID>
<Version>BISON 8.1.0.0</Version>
<DossierName>%(dossiername)s</DossierName>
<Timestamp>%(timestamp)s</Timestamp>
<%(dossiername)s>
%(content)s
</%(dossiername)s>
</VV_TM_PUSH>""" % data

        return xml

    def push(self, remote, namespace, dossier, path, content):
        # Add content
        self.namespace = namespace
        self.dossiername = dossier
        self.content = content
        # Calculate XML with wrapper/header
        content = str(self)
        if settings.GOVI_PUSH_DEBUG:
            self.log.debug(content)

        response_code = -1
        response_content = None
        error = False
        if settings.GOVI_PUSH_SEND:
            self.log.debug("Posting to %s/%s" % (remote, path))
            try:
                conn = httplib.HTTPConnection(remote, timeout=settings.GOVI_PUSH_TIMEOUT)
                conn.request("POST", path, content, {"Content-type": "application/xml"})
            except socket.timeout:
                error = True
                self.log.error("Got timeout while connecting")
            except (httplib.HTTPException, socket.error) as ex:
                error = True
                self.log.error("Got exception while connecting: %s" % ex)

            if not error:
                response = conn.getresponse()
                response_code = response.status
                response_content = response.read()
                conn.close()

            if settings.GOVI_PUSH_DEBUG:
                self.log.debug("Got response code %s and content: %s" % (response_code, response_content))

        return (response_code,response_content)
