"""
Convert the KV15 and KV17 payloads we push into SIRI-SX (SIRI 2.1+) situations.

The input is the same XML we hand to Push (the fragments rendered from xml/kv15*.xml and xml/kv17journey.xml),
so every caller of push_message gets a SIRI-SX variant without having to know about it.

Mapping, loosely following https://github.com/EmmaKnijn/kv-to-sx/blob/main/mapping.toml
(target paths are relative to PtSituationElement):

KV15 STOPMESSAGE
    dataownercode                           -> ParticipantRef
    dataownercode/messagecodedate/number    -> SituationNumber (KV15:<dataowner>:<date>:<number>)
    messagetimestamp                        -> CreationTime
    messagestarttime / messageendtime       -> ValidityPeriod/StartTime, ValidityPeriod/EndTime
    reasontype                              -> AlertCause (coarse, see REASONTYPE_ALERTCAUSE)
    reasoncontent                           -> ReasonName
    messagepriority                         -> Severity (CALAMITY is severe, everything else normal)
    messagecontent                          -> Summary, Description
    effectcontent, measurecontent           -> Detail
    advicecontent                           -> Advice
    userstopcode (+ lineplanningnumber)     -> Affects/StopPoints/AffectedStopPoint/StopPointRef (+ Lines/AffectedLine)

Stop refs are the CHB quay (NL:CHB:Quay:32009006), made from the quay code imported from RID into
Kv1Stop.quaycoderef (NL:Q:32009006). Quay codes outside the CHB (DE:Q:, BE:Q:) are used as is, and we fall back to the
bare userstopcode if we don't have one. Line and journey refs are the bare lineplanningnumber and journeynumber, as
most operators' own SIRI-ET/VM feeds use. The operator is in ParticipantRef.
KV15 DELETEMESSAGE                          -> the same SituationNumber with Progress closed

KV17 KV17JOURNEY                            -> SituationNumber (KV17:<dataowner>:<operatingday>:<line>:<journey>)
                                               and Affects (operator, line or vehicle journey)
     KV17MUTATEJOURNEY/CANCEL               -> open situation, reason/advice content as Detail/Advice
     KV17MUTATEJOURNEY/RECOVER              -> closed situation
     KV17MUTATEJOURNEY/NOTMONITORED         -> nothing, this isn't passenger information
     KV17MUTATEJOURNEYSTOP/SHORTEN          -> AffectedVehicleJourney/Calls/Call per skipped stop
     KV17MUTATEJOURNEYSTOP/MUTATIONMESSAGE  -> AffectedVehicleJourney/Calls/Call, reason/advice content as Detail/Advice
"""
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import now, make_aware
from lxml import etree

from kv1.models import Kv1Stop

SIRI_NAMESPACE = 'http://www.siri.org.uk/siri'
SIRI_SX_PATH = '/OPENOV/SituationExchangeDelivery'  # Default endpoint (topic) to push to
SIRI_VERSION = '2.1'
LANGUAGE = 'nl'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
CHB_QUAYCODE_PREFIX = 'NL:Q:'  # Kv1Stop.quaycoderef as imported from RID
CHB_QUAY_PREFIX = 'NL:CHB:Quay:'  # What we send

# KV15 reasontype -> SIRI AlertCause. The KV subreasontypes aren't unique across reasontypes, so we stay coarse
REASONTYPE_ALERTCAUSE = {
    '1': 'miscellaneous',
    '2': 'undefinedPersonnelProblem',
    '3': 'undefinedEquipmentProblem',
    '4': 'undefinedEnvironmentalProblem',
}

log = logging.getLogger('openebs.siri_sx')


def to_siri_sx(dossier, content, producer_ref):
    """
    Convert the KV content of a push (a string or list of strings with KV fragments) into a SIRI-SX
    ServiceDelivery. Returns None if there's nothing to tell in SIRI-SX.
    """
    situations = convert(dossier, content)
    if len(situations) == 0:
        return None

    timestamp = now().isoformat()
    siri = etree.Element(_tag('Siri'), nsmap={None: SIRI_NAMESPACE}, version=SIRI_VERSION)
    delivery = _sub(siri, 'ServiceDelivery')
    _sub(delivery, 'ResponseTimestamp', timestamp)
    _sub(delivery, 'ProducerRef', producer_ref)
    sx = _sub(delivery, 'SituationExchangeDelivery', version=SIRI_VERSION)
    _sub(sx, 'ResponseTimestamp', timestamp)
    container = _sub(sx, 'Situations')
    for situation in situations:
        container.append(situation)
    return etree.tostring(siri, pretty_print=True, xml_declaration=True, encoding='UTF-8')


def convert(dossier, content):
    """ Return a list of PtSituationElements for the KV content """
    if isinstance(content, list):
        content = "".join(content)
    if content is None or content.strip() == "":
        return []
    root = etree.fromstring("<root>%s</root>" % content)
    refs = RefLookup(root)

    if dossier == 'KV15messages':
        return [s for s in (_convert_kv15(message, refs) for message in root) if s is not None]
    elif dossier == 'KV17cvlinfo':
        return [s for s in (_convert_kv17(group, refs) for group in _group_kv17(root)) if s is not None]
    log.warning("Don't know how to convert %s to SIRI-SX" % dossier)
    return []


# KV15

def _convert_kv15(message, refs):
    dataowner = _text(message, 'dataownercode')
    situation_number = "KV15:%s:%s:%s" % (dataowner, _text(message, 'messagecodedate'),
                                          _text(message, 'messagecodenumber'))

    if message.tag == 'DELETEMESSAGE':
        start = _start_of_day(parse_date(_text(message, 'messagecodedate')))
        return _situation(now(), dataowner, situation_number, 'closed', start, now())

    if message.tag != 'STOPMESSAGE':
        log.warning("Unknown KV15 message type %s, not converting to SIRI-SX" % message.tag)
        return None

    lines = [line.text for line in message.iterfind('lineplanningnumbers/lineplanningnumber')]
    situation = _situation(_datetime(message, 'messagetimestamp') or now(), dataowner, situation_number, 'open',
                           _datetime(message, 'messagestarttime') or now(), _datetime(message, 'messageendtime'),
                           reasontype=_text(message, 'reasontype'),
                           reason=_text(message, 'reasoncontent'),
                           severity='severe' if _text(message, 'messagepriority') == 'CALAMITY' else 'normal',
                           summary=_text(message, 'messagecontent'),
                           description=_text(message, 'messagecontent'),
                           detail=_join(_text(message, 'effectcontent'), _text(message, 'measurecontent')),
                           advice=_text(message, 'advicecontent'))

    stop_points = _sub(_sub(situation, 'Affects'), 'StopPoints')
    for userstopcode in message.iterfind('userstopcodes/userstopcode'):
        stop = _sub(stop_points, 'AffectedStopPoint')
        _sub(stop, 'StopPointRef', refs.stop(dataowner, userstopcode.text))
        if len(lines) > 0:
            affected_lines = _sub(stop, 'Lines')
            for line in lines:
                _sub(_sub(affected_lines, 'AffectedLine'), 'LineRef', line)
    return situation


# KV17

def _group_kv17(root):
    """ A KV17JOURNEY is followed by the mutations belonging to it, possibly many journeys in one push """
    groups = []
    for element in root:
        if element.tag == 'KV17JOURNEY':
            groups.append({'journey': element})
        elif len(groups) > 0:
            groups[-1][element.tag] = element
        else:
            log.warning("Got %s without KV17JOURNEY, not converting to SIRI-SX" % element.tag)
    return groups


def _convert_kv17(group, refs):
    journey = group['journey']
    mutate_journey = group.get('KV17MUTATEJOURNEY')
    mutate_stops = group.get('KV17MUTATEJOURNEYSTOP')

    cancel = mutate_journey.find('CANCEL') if mutate_journey is not None else None
    recover = mutate_journey.find('RECOVER') if mutate_journey is not None else None
    stop_mutations = list(mutate_stops) if mutate_stops is not None else []
    stop_mutations = [m for m in stop_mutations if m.tag in ('SHORTEN', 'MUTATIONMESSAGE')]
    if cancel is None and recover is None and len(stop_mutations) == 0:
        return None  # Only NOTMONITORED, no passenger information there

    dataowner = _text(journey, 'dataownercode')
    operatingday = parse_date(_text(journey, 'operatingday'))
    line = _text(journey, 'lineplanningnumber')
    journeynumber = _text(journey, 'journeynumber')
    if journey.find('allLines') is not None:
        scope = 'ALL'
    elif journey.find('allJourneysOfLine') is not None:
        scope = "%s:ALL" % line
    else:
        scope = "%s:%s" % (line, journeynumber)
    begintime = _text(journey, 'begintime')
    situation_number = "KV17:%s:%s:%s" % (dataowner, operatingday.isoformat(), scope)
    if begintime:
        situation_number += ":%s" % begintime

    start = _time_32h(operatingday, begintime) if begintime else _start_of_day(operatingday)
    endtime = _text(journey, 'endtime')
    end = _time_32h(operatingday, endtime) if endtime else _end_of_operating_day(operatingday)

    timestamp_source = mutate_journey if mutate_journey is not None else mutate_stops
    timestamp = _datetime(timestamp_source, 'timestamp') or now()

    if recover is not None:
        situation = _situation(timestamp, dataowner, situation_number, 'closed', start, end)
    else:
        details = cancel if cancel is not None else stop_mutations[0]
        if cancel is not None:
            summary = _cancel_summary(journey, dataowner, line)
        elif any(m.tag == 'SHORTEN' for m in stop_mutations):
            summary = "Rit rijdt niet langs alle haltes"
        else:
            summary = _text(details, 'reasoncontent') or "Wijziging in de dienstregeling"
        situation = _situation(timestamp, dataowner, situation_number, 'open', start, end,
                               reasontype=_text(details, 'reasontype'),
                               reason=_text(details, 'reasoncontent'),
                               summary=summary,
                               detail=_text(details, 'reasoncontent'),
                               advice=_text(details, 'advicecontent'))

    affects = _sub(situation, 'Affects')
    if journey.find('allLines') is not None:
        _sub(_sub(_sub(affects, 'Operators'), 'AffectedOperator'), 'OperatorRef', dataowner)
    elif journey.find('allJourneysOfLine') is not None:
        network = _sub(_sub(affects, 'Networks'), 'AffectedNetwork')
        _sub(_sub(network, 'AffectedLine'), 'LineRef', line)
    else:
        vehicle_journey = _sub(_sub(affects, 'VehicleJourneys'), 'AffectedVehicleJourney')
        framed = _sub(vehicle_journey, 'FramedVehicleJourneyRef')
        _sub(framed, 'DataFrameRef', operatingday.isoformat())
        _sub(framed, 'DatedVehicleJourneyRef', journeynumber)
        _sub(vehicle_journey, 'LineRef', line)
        # A cancel affects the whole journey, only list the stops if those are all that changed
        if cancel is None and recover is None and len(stop_mutations) > 0:
            calls = _sub(vehicle_journey, 'Calls')
            for mutation in stop_mutations:
                call = _sub(calls, 'Call')
                _sub(call, 'StopPointRef', refs.stop(dataowner, _text(mutation, 'userstopcode')))
                _sub(call, 'Order', _text(mutation, 'passagesequencenumber'))
    return situation


def _cancel_summary(journey, dataowner, line):
    if journey.find('allLines') is not None:
        return "Alle ritten van %s vervallen" % dataowner
    elif journey.find('allJourneysOfLine') is not None:
        return "Alle ritten van lijn %s vervallen" % line
    return "Rit vervalt"


# SIRI building blocks

def _situation(created, dataowner, situation_number, progress, start, end, reasontype=None, reason=None,
               severity='normal', summary=None, description=None, detail=None, advice=None):
    """ Create a PtSituationElement up to (but not including) Affects, in the order the XSD requires """
    situation = etree.Element(_tag('PtSituationElement'))
    _sub(situation, 'CreationTime', created.isoformat())
    _sub(situation, 'ParticipantRef', dataowner)
    _sub(situation, 'SituationNumber', situation_number)
    _sub(_sub(situation, 'Source'), 'SourceType', 'directReport')
    _sub(situation, 'Progress', progress)
    validity = _sub(situation, 'ValidityPeriod')
    _sub(validity, 'StartTime', start.isoformat())
    if end is not None:
        _sub(validity, 'EndTime', end.isoformat())
    _sub(situation, 'AlertCause', REASONTYPE_ALERTCAUSE.get(reasontype, 'unknown'))
    _text_sub(situation, 'ReasonName', reason)
    _sub(situation, 'Severity', severity)
    _sub(situation, 'Language', LANGUAGE)
    _text_sub(situation, 'Summary', summary)
    _text_sub(situation, 'Description', description)
    _text_sub(situation, 'Detail', detail)
    _text_sub(situation, 'Advice', advice)
    return situation


class RefLookup(object):
    """
    Find the quay codes for all stops in a push with a query per dataowner, falling back to the userstopcode
    """
    def __init__(self, root):
        stops = set()
        for message in root:
            dataowner = _text(message, 'dataownercode')
            if dataowner is None:
                continue
            stops.update((dataowner, code.text.strip()) for code in message.iter('userstopcode') if code.text)
        # KV17 mutations don't repeat the dataowner, they follow the KV17JOURNEY that has it
        dataowner = None
        for element in root:
            dataowner = _text(element, 'dataownercode') or dataowner
            if element.tag == 'KV17MUTATEJOURNEYSTOP':
                stops.update((dataowner, code.text.strip()) for code in element.iter('userstopcode') if code.text)

        self.stops = {}
        for dataowner in set(d for d, _ in stops):
            rows = Kv1Stop.objects.filter(dataownercode=dataowner, quaycoderef__isnull=False,
                                          userstopcode__in=[c for d, c in stops if d == dataowner]) \
                .exclude(quaycoderef='')
            self.stops.update({(dataowner, code): self.quay_ref(ref)
                               for code, ref in rows.values_list('userstopcode', 'quaycoderef')})

    @staticmethod
    def quay_ref(quaycode):
        """ NL:Q:32009006 -> NL:CHB:Quay:32009006, other quay codes aren't in the CHB """
        if quaycode.startswith(CHB_QUAYCODE_PREFIX):
            return CHB_QUAY_PREFIX + quaycode[len(CHB_QUAYCODE_PREFIX):]
        return quaycode

    def stop(self, dataowner, userstopcode):
        return self.stops.get((dataowner, userstopcode), userstopcode)


def _start_of_day(day):
    return make_aware(datetime.combine(day, datetime.min.time()))


def _end_of_operating_day(day):
    return _start_of_day(day) + timedelta(days=1, hours=settings.CROSSOVER_HOUR)


def _time_32h(day, time):
    """ KV17 times may go past 24:00 to stay on the same operating day """
    hours, minutes, seconds = [int(part) for part in time.split(':')]
    return _start_of_day(day) + timedelta(hours=hours, minutes=minutes, seconds=seconds)


def _join(*texts):
    texts = [text for text in texts if text]
    return "\n".join(texts) if len(texts) > 0 else None


def _datetime(element, path):
    text = _text(element, path)
    try:
        return parse_datetime(text) if text else None
    except ValueError:
        return None


def _text(element, path):
    found = element.find(path)
    if found is None or found.text is None:
        return None
    text = found.text.strip()
    return text if text != "" else None


def _tag(name):
    return "{%s}%s" % (SIRI_NAMESPACE, name)


def _sub(parent, name, text=None, **attributes):
    element = etree.SubElement(parent, _tag(name), **attributes)
    if text is not None:
        element.text = text
    return element


def _text_sub(parent, name, text):
    if text:
        _sub(parent, name, text, **{XML_LANG: LANGUAGE})
