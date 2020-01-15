import http.client
import logging
import socket

from django.utils.timezone import now
from lxml import etree


class Push:
    alias = None
    timeout = 10
    enabled = True
    fail_on_failure = False
    debug = True

    def __init__(self, host, endpoint, namespace, dossiername, subscriberid = 'openOV', use_https = False):
        self.log = logging.getLogger("openebs.push")
        self.host = host
        self.endpoint = endpoint
        self.subscriberid = subscriberid
        self.namespace = namespace
        self.dossiername = dossiername
        self.timestamp = now()
        self.use_https = use_https

    def __str__(self):
        data = {'namespace': self.namespace,
                'subscriberid': self.subscriberid,
                'dossiername': self.dossiername,
                'timestamp':self.timestamp.isoformat('T'),
                'content' : self.content
                }

        wrapper = """<%(dossiername)s>
        %(content)s
        </%(dossiername)s>"""

        # If we have list, wrap each item in the dossiername
        final_content = ""
        if isinstance(self.content, list):
            for item in self.content:
                final_content += wrapper % {'dossiername': data['dossiername'],
                                            'content': item.replace('\n', '')}
        else:
            final_content = wrapper % data
        data['content'] = final_content

        xml = """<VV_TM_PUSH xmlns="%(namespace)s">
<SubscriberID>%(subscriberid)s</SubscriberID>
<Version>BISON 8.1.0.0</Version>
<DossierName>%(dossiername)s</DossierName>
<Timestamp>%(timestamp)s</Timestamp>
%(content)s
</VV_TM_PUSH>""" % data

        return etree.tostring(etree.XML(xml), pretty_print=True)

    def push(self, content):
        # Add content
        # TODO What this do?
        self.content = content

        # Calculate XML with wrapper/header
        content = self.__str__()
        if self.debug:
            self.log.debug("Pushing message:\n"+content)

        response_code = -1
        response_content = None
        error = False
        if self.enabled:
            self.log.debug("Posting to %s (%s://%s%s)" % (self.alias, 'https' if self.use_https else 'http', self.host, self.endpoint, ))
            conn = None
            try:
                if self.use_https:
                    conn = httplib.HTTPSConnection(self.host, timeout=self.timeout, port=443)
                else:
                    conn = httplib.HTTPConnection(self.host, timeout=self.timeout)
                conn.request("POST", self.endpoint, content, {"Content-type": "application/xml"})
            except socket.timeout:
                error = True
                self.log.error("Got timeout while connecting to %s" % self.alias)
            except (httplib.HTTPException, socket.error) as ex:
                error = True
                self.log.error("Got exception while connecting to %s: %s" % (self.alias, ex))

            if not error and conn is not None:
                response = conn.getresponse()
                response_code = response.status
                response_content = response.read()
                conn.close()

            if self.debug:
                self.log.debug("Connecting to %s and got response code %s and content: %s" % (self.alias, response_code, response_content))

        return response_code, response_content
