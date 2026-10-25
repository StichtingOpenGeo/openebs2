"""
Convert the KV15 and KV17 payloads we push into SIRI-SX (SIRI 2.1+) situations.

The input is the same XML we hand to Push (the fragments rendered from xml/kv15*.xml and xml/kv17journey.xml),
so every caller of push_message gets a SIRI-SX variant without having to know about it.

Mapping, loosely following https://github.com/EmmaKnijn/kv-to-sx/blob/main/mapping.toml
(target paths are relative to PtSituationElement):

KV15 STOPMESSAGE
    dataownercode                           -> ParticipantRef (NL:BISON:Codespace:<dataowner>)
    dataownercode/messagecodedate/number    -> SituationNumber (KV15:<dataowner>:<date>:<number>)
    messagetimestamp                        -> CreationTime
    messagestarttime / messageendtime       -> ValidityPeriod/StartTime, ValidityPeriod/EndTime
    reasontype/subreasontype                -> AlertCause and PublicEventReason (see SUBREASONTYPE_ALERTCAUSE)
    reasoncontent                           -> ReasonName
    messagepriority                         -> Severity and Priority (CALAMITY is severe/1, everything else normal/3)
    messagecontent                          -> Summary, Description
    effectcontent, measurecontent           -> Detail
    advicecontent                           -> Advice
    userstopcode (+ lineplanningnumber)     -> Affects/StopPoints/AffectedStopPoint/StopPointRef (+ Lines/AffectedLine)

Stop refs are the CHB quay (NL:CHB:Quay:32009006), made from the quay code imported from RID into
Kv1Stop.quaycoderef (NL:Q:32009006). Quay codes outside the CHB (DE:Q:, BE:Q:) are used as is, and we fall back to the
bare userstopcode if we don't have one. Lines are the NeTEx line ref imported from RID into Kv1Line.original_ref
(NL:HTM:Line:1), falling back to NL:<dataowner>:Line:<lineplanningnumber>. Journeys are the bare journeynumber.
The dataowner is the codespace, so ParticipantRef and OperatorRef are NL:BISON:Codespace:<dataowner> and the
ProducerRef of a delivery is NL:<dataowner> (if it's all one dataowner).

Every situation also gets CountryRef, PublicationWindow, Priority, ReportType (incident for a calamity, otherwise
general) and Planned (true for works and events), like the NS samples of the Dutch profile. Enumerations only use
the values the SIRI-NL profile allows.

KV15 DELETEMESSAGE                          -> the same SituationNumber with Progress closed

KV17 KV17JOURNEY                            -> SituationNumber (KV17:<dataowner>:<operatingday>:<line>:<journey>)
                                               and Affects (operator, line or vehicle journey)
     KV17MUTATEJOURNEY/CANCEL               -> open situation, reason/advice content as Detail/Advice, and a
                                               Consequence for what is cancelled: tripCancellation, lineCancellation
                                               or (all lines) discontinuedOperation
     KV17MUTATEJOURNEY/RECOVER              -> closed situation
     KV17MUTATEJOURNEY/NOTMONITORED         -> nothing, this isn't passenger information
     KV17MUTATEJOURNEYSTOP/SHORTEN          -> AffectedVehicleJourney/Calls/Call per skipped stop, and a Consequence
                                               (stopCancelled) for those
     KV17MUTATEJOURNEYSTOP/MUTATIONMESSAGE  -> AffectedVehicleJourney/Calls/Call, reason/advice content as Detail/Advice
"""
import logging
from copy import deepcopy
from datetime import datetime, timedelta

from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import now, make_aware
from lxml import etree

from kv1.models import Kv1Line, Kv1Stop

SIRI_NAMESPACE = 'http://www.siri.org.uk/siri'
SIRI_SX_PATH = '/OPENOV/SituationExchangeDelivery'  # Default endpoint (topic) to push to
SIRI_VERSION = '2.1'
LANGUAGE = 'nl'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
COUNTRY = 'nl'
PARTICIPANT_PREFIX = 'NL:BISON:Codespace:'
CHB_QUAYCODE_PREFIX = 'NL:Q:'  # Kv1Stop.quaycoderef as imported from RID
CHB_QUAY_PREFIX = 'NL:CHB:Quay:'  # What we send

# KV15/KV17 subreasontype -> SIRI AlertCause, limited to the values the SIRI-NL profile allows. The KV codes are the old
# TPEG Pti19-22 codes, one table per reasontype (1 miscellaneous, 2 personnel, 3 equipment, 4 environment), so a few
# codes mean different things per reasontype. The UI shows one flat list of subreasons though, so a code with a
# single meaning in that list is mapped on its own, and only the shared codes go by reasontype.
SUBREASONTYPE_ALERTCAUSE = {
    '0_1': 'previousDisturbances',  # Eerdere verstoring
    '3': 'heavySnowFall',  # Sneeuw
    '3_1': 'policeOrder',  # Op last van de politie
    '3_9': 'securityAlert',  # Bommelding
    '3_11': 'evacuation',  # Ontruiming
    '3_15': 'bombDisposal',  # Ruimen WO II bom
    '3_17': 'fireBrigadeOrder',  # Op last van de brandweer
    '4': {'1': 'fire', '2': 'staffAbsence', '3': 'signalFailure', '4': 'fire'},  # Brand, Tekort aan personeel, Seinstoring
    '4_1': 'signalFailure',  # Sein en wisselstoring, like NS does
    '5': {'2': 'industrialAction', '3': 'derailment', '4': 'strongWinds'},  # Staking/Vakbondsacties, Ontsporing, Storm
    '5_1': 'industrialAction',  # Mogelijke staking
    '6': {'1': 'accident', '2': 'industrialAction', '3': 'accident', '4': 'accident'},  # Ongeval, Stiptheidsactie
    '6_2': 'defectiveVehicle',  # Defecte trein
    '6_3': 'personHitByVehicle',  # Aanrijding met een persoon
    '6_4': 'emergencyMedicalServices',  # Passagier onwel
    '6_6': 'collision',  # Aanrijding
    '7': {'1': 'overcrowded', '2': 'overcrowded', '3': 'breakDown', '4': 'overcrowded'},  # Extreme drukte, Defect materieel
    '8_1': 'brokenRail',  # Defect spoor
    '8_4': 'miscellaneous',  # Tekort aan materieel
    '8_10': 'pointsFailure',  # Wisselstoring
    '8_11': 'levelCrossingFailure',  # Overwegstoring
    '8_12': 'trafficManagementSystemFailure',  # Storing in verkeersleidingsysteem
    '8_13': 'poorRailConditions',  # Gladde sporen
    '9': 'repairWork',  # Herstelwerkzaamheden
    '9_1': 'ice',  # Gladheid
    '9_2': 'ice',  # IJsgang, IJzel
    '11': 'maintenanceWork',  # Herstel werkzaamheden
    '11_2': 'maintenanceWork',  # Uitloop herstelwerkzaamheden
    '12': 'powerProblem',  # Stroomstoring
    '12_1': 'overheadWireFailure',  # Defecte bovenleiding
    '12_2': 'maintenanceWork',  # Uitloop werkzaamheden
    '14': {'3': 'swingBridgeFailure', '4': 'flooding'},  # Defecte brug, Wateroverlast
    '14_1': 'bridgeDamage',  # Defect viaduct
    '15': 'congestion',  # File
    '16': 'routeBlockage',  # Route versperd, Stremming
    '17': 'personOnTheLine',  # Mensen op de route
    '18': 'vehicleOnTheLine',  # Auto in spoor
    '19_1': 'fallenTreeOnTheLine',  # Omgevallen bomen
    '20': 'animalOnTheLine',  # Vee op de route
    '23': 'roadworks',  # Werkzaamheden
    '23_1': 'sewerageMaintenance',  # Rioleringswerkzaamheden
    '23_2': 'roadworks',  # Wegwerkzaamheden
    '23_3': 'roadworks',  # Asfalteringswerkzaamheden
    '23_4': 'roadworks',  # Bestratingswerkzaamheden
    '24_1': 'procession',  # Optocht
    '26_1': 'speedRestrictions',  # Snelheidsbeperkingen
    '26_2': 'miscellaneous',  # Logistieke problemen
    '255': {'4': 'poorWeather'},  # Onbekend, Weersomstandigheden
    '255_1': 'lightningStrike',  # Blikseminslag
}
# Events (24_x) are a specialEvent, with the kind of event as PublicEventReason if the profile has it
SUBREASONTYPE_PUBLICEVENT = {
    '24_1': 'procession',  # Optocht
    '24_6': 'flowerEvent',  # Bloemencorso
    '24_7': 'streetFestival',  # Braderie
    '24_8': 'festival',  # Carnaval
    '24_9': 'market',  # Jaarmarkt
    '24_10': 'funfair',  # Kermis
    '24_11': 'stateOccasion',  # Koninginnedag
    '24_12': 'marathon',  # Marathon
    '24_13': 'bicycleRace',  # Wielerronde
    '24_14': 'footballMatch',  # Voetbalwedstrijd
    '24_15': 'ceremonialEvent',  # Herdenking
    '24_16': 'sportsMeeting',  # Avondvierdaagse
}
# Without a (known) subreasontype. The profile doesn't allow the undefined...Problem values per reasontype
REASONTYPE_ALERTCAUSE = {
    '1': 'miscellaneous',
    '3': 'technicalProblem',
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

    # A push is normally for one operator, which is then the producer
    participants = set(s.findtext(_tag('ParticipantRef')) for s in situations)
    if len(participants) == 1:
        producer_ref = "NL:%s" % participants.pop()[len(PARTICIPANT_PREFIX):]

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
                           subreasontype=_text(message, 'subreasontype'),
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
                _sub(_sub(affected_lines, 'AffectedLine'), 'LineRef', refs.line(dataowner, line))
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
                               subreasontype=_text(details, 'subreasontype'),
                               reason=_text(details, 'reasoncontent'),
                               summary=summary,
                               detail=_text(details, 'reasoncontent'),
                               advice=_text(details, 'advicecontent'))

    affects = _sub(situation, 'Affects')
    if journey.find('allLines') is not None:
        _sub(_sub(_sub(affects, 'Operators'), 'AffectedOperator'), 'OperatorRef', PARTICIPANT_PREFIX + dataowner)
    elif journey.find('allJourneysOfLine') is not None:
        network = _sub(_sub(affects, 'Networks'), 'AffectedNetwork')
        _sub(_sub(network, 'AffectedLine'), 'LineRef', refs.line(dataowner, line))
    else:
        vehicle_journey = _sub(_sub(affects, 'VehicleJourneys'), 'AffectedVehicleJourney')
        framed = _sub(vehicle_journey, 'FramedVehicleJourneyRef')
        _sub(framed, 'DataFrameRef', operatingday.isoformat())
        _sub(framed, 'DatedVehicleJourneyRef', journeynumber)
        _sub(vehicle_journey, 'LineRef', refs.line(dataowner, line))
        # A cancel affects the whole journey, only list the stops if those are all that changed
        if cancel is None and recover is None and len(stop_mutations) > 0:
            calls = _sub(vehicle_journey, 'Calls')
            for mutation in stop_mutations:
                call = _sub(calls, 'Call')
                # passagesequencenumber counts earlier visits to the stop, it isn't the Order in the journey
                _sub(call, 'StopPointRef', refs.stop(dataowner, _text(mutation, 'userstopcode')))

    if cancel is not None:
        if journey.find('allLines') is not None:
            condition = 'discontinuedOperation'
        elif journey.find('allJourneysOfLine') is not None:
            condition = 'lineCancellation'
        else:
            condition = 'tripCancellation'
        consequence = _sub(_sub(situation, 'Consequences'), 'Consequence')
        _sub(consequence, 'Condition', condition)
        consequence.append(deepcopy(affects))
    elif recover is None and journey.find('journeynumber') is not None:
        shortened = [m for m in stop_mutations if m.tag == 'SHORTEN']
        if len(shortened) > 0:
            # Only the skipped stops, a MUTATIONMESSAGE stop is still served
            consequence = _sub(_sub(situation, 'Consequences'), 'Consequence')
            _sub(consequence, 'Condition', 'stopCancelled')
            skipped = set(refs.stop(dataowner, _text(m, 'userstopcode')) for m in shortened)
            consequence_affects = deepcopy(affects)
            for call in list(consequence_affects.iter(_tag('Call'))):
                if call.findtext(_tag('StopPointRef')) not in skipped:
                    call.getparent().remove(call)
            consequence.append(consequence_affects)
    return situation


def _cancel_summary(journey, dataowner, line):
    if journey.find('allLines') is not None:
        return "Alle ritten van %s vervallen" % dataowner
    elif journey.find('allJourneysOfLine') is not None:
        return "Alle ritten van lijn %s vervallen" % line
    return "Rit vervalt"


# SIRI building blocks

def _situation(created, dataowner, situation_number, progress, start, end, reasontype=None, subreasontype=None,
               reason=None, severity='normal', summary=None, description=None, detail=None, advice=None):
    """ Create a PtSituationElement up to (but not including) Affects, in the order the XSD requires """
    published = now()
    situation = etree.Element(_tag('PtSituationElement'))
    _sub(situation, 'CreationTime', created.isoformat())
    _sub(situation, 'CountryRef', COUNTRY)
    _sub(situation, 'ParticipantRef', PARTICIPANT_PREFIX + dataowner)
    _sub(situation, 'SituationNumber', situation_number)
    # The profile requires it. We don't track versions: a KV15 edit closes the old situation and opens a new one
    _sub(situation, 'Version', '1')
    _sub(_sub(situation, 'Source'), 'SourceType', 'directReport')
    _sub(situation, 'Progress', progress)
    validity = _sub(situation, 'ValidityPeriod')
    _sub(validity, 'StartTime', start.isoformat())
    if end is not None:
        _sub(validity, 'EndTime', end.isoformat())
    # From now until the end, or nothing more to show if it's closed
    publication = _sub(situation, 'PublicationWindow')
    _sub(publication, 'StartTime', published.isoformat())
    if progress == 'closed':
        _sub(publication, 'EndTime', published.isoformat())
    elif end is not None:
        _sub(publication, 'EndTime', end.isoformat())
    _sub(situation, 'AlertCause', _alert_cause(reasontype, subreasontype))
    if subreasontype in SUBREASONTYPE_PUBLICEVENT:
        _sub(situation, 'PublicEventReason', SUBREASONTYPE_PUBLICEVENT[subreasontype])
    _text_sub(situation, 'ReasonName', reason)
    _sub(situation, 'Severity', severity)
    _sub(situation, 'Priority', '1' if severity == 'severe' else '3')
    # Only a calamity (the one thing that makes it severe) is an incident, everything else is general information
    _sub(situation, 'ReportType', 'incident' if severity == 'severe' else 'general')
    # Works and events are planned, KV doesn't tell us otherwise
    _sub(situation, 'Planned', 'true' if (subreasontype or '').startswith(('23', '24')) else 'false')
    _sub(situation, 'Language', LANGUAGE)
    _text_sub(situation, 'Summary', summary)
    _text_sub(situation, 'Description', description)
    _text_sub(situation, 'Detail', detail)
    _text_sub(situation, 'Advice', advice)
    return situation


def _alert_cause(reasontype, subreasontype):
    cause = SUBREASONTYPE_ALERTCAUSE.get(subreasontype)
    if isinstance(cause, dict):
        cause = cause.get(reasontype)
    if cause is None and (subreasontype or '').startswith('24_'):
        cause = 'specialEvent'
    return cause or REASONTYPE_ALERTCAUSE.get(reasontype, 'unknown')


class RefLookup(object):
    """
    Find the quay codes for all stops and the NeTEx refs for all lines in a push, with a query per dataowner
    """
    def __init__(self, root):
        stops = set()
        lines = set()
        for message in root:
            dataowner = _text(message, 'dataownercode')
            if dataowner is None:
                continue
            stops.update((dataowner, code.text.strip()) for code in message.iter('userstopcode') if code.text)
            lines.update((dataowner, code.text.strip()) for code in message.iter('lineplanningnumber') if code.text)
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

        self.lines = {}
        for dataowner in set(d for d, _ in lines):
            rows = Kv1Line.objects.filter(dataownercode=dataowner, original_ref__isnull=False,
                                          lineplanningnumber__in=[c for d, c in lines if d == dataowner]) \
                .exclude(original_ref='')
            self.lines.update({(dataowner, code): ref
                               for code, ref in rows.values_list('lineplanningnumber', 'original_ref')})

    @staticmethod
    def quay_ref(quaycode):
        """ NL:Q:32009006 -> NL:CHB:Quay:32009006, other quay codes aren't in the CHB """
        if quaycode.startswith(CHB_QUAYCODE_PREFIX):
            return CHB_QUAY_PREFIX + quaycode[len(CHB_QUAYCODE_PREFIX):]
        return quaycode

    def stop(self, dataowner, userstopcode):
        return self.stops.get((dataowner, userstopcode), userstopcode)

    def line(self, dataowner, lineplanningnumber):
        return self.lines.get((dataowner, lineplanningnumber),
                              "NL:%s:Line:%s" % (dataowner, lineplanningnumber))


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
