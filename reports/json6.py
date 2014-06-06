import xml.etree.cElementTree as ET

def stripschema(tag):
    return tag.split('}')[-1]

def get_elem_text(message, needle):
    ints = ['journeynumber', 'reinforcementnumber', 'passagesequencenumber', 'vehiclenumber', 'punctuality', 'blockcode', 'numberofcoaches', 
'distancesincelastuserstop', 'rd-x', 'rd-y']

    elem = message.find('{http://bison.connekt.nl/tmi8/kv6/msg}'+needle)
    if elem is not None:
        if needle in ints:
            if (needle == 'rd-x' or needle == 'rd-y') and elem.text == '-1':
                return None
            else:
                return int(elem.text)
        elif needle == 'wheelchairaccessible':
            return elem.text == 'ACCESSIBLE'
        else:
            return elem.text
    else:
        return elem

def parseKV6(message, message_type, needles=[]):
    result = {'messagetype': message_type}

    for needle in needles:
        result[needle.replace('-', '_')] = get_elem_text(message, needle)

    return result


def fetchfrommessage(message):
    message_type = stripschema(message.tag)

    required = ['dataownercode', 'lineplanningnumber', 'operatingday', 'journeynumber', 'reinforcementnumber', 'timestamp', 'source']

    if message_type == 'DELAY':
        return parseKV6(message, message_type, required + ['punctuality'])
    elif message_type == 'INIT':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'blockcode', 
'wheelchairaccessible', 'numberofcoaches'])
    elif message_type in ['ARRIVAL', 'ONSTOP', 'DEPARTURE']:
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'punctuality'])
    elif message_type == 'ONROUTE':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'punctuality', 
'distancesincelastuserstop', 'rd-x', 'rd-y'])
    elif message_type == 'OFFROUTE':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'rd-x', 'rd-y'])
    elif message_type == 'END':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber'])
    return None

def kv6_807to810(xml):
    item = {}
    item['dataownercode'] = xml.find('DataOwnerCode').text
    punctuality = xml.find('Punctuality').text
    if punctuality is not None:
        item['punctuality'] = int(punctuality)
    else:
        item['punctuality'] = None
    item['vehiclenumber'] = int(xml.find('VehicleIDNumber').text)
    item['userstopcode'] = xml.find('USRStopCode').text
    item['blockcode'] = int(xml.find('BlockCode').text)
    item['journeynumber'] = int(xml.find('JourneyNumber').text)
    item['lineplanningnumber'] = xml.find('PlanningLineNumber').text
    item['operatingday'] = xml.find('OperatingDate').text
    item['timestamp'] = xml.find('TimeStampSourceSystem').text
    item['reinforcementnumber'] = int(xml.find('FortifyOrderNumber').text)
    distance = xml.find('DistanceSinceLastStop').text
    if distance is not None:
        item['distancesincelastuserstop'] = int(distance)
    else:
        item['distancesincelastuserstop'] = None
    if 'userstopcode' in item:
        item['passagesequencenumber'] = 0
    rd_x = xml.find('RD_X').text
    rd_y = xml.find('RD_Y').text
    if rd_x in ['0','-1']:
        item['rd_x'] = None
    if rd_y in ['0','-1']:
        item['rd_y'] = None
    tripstatus = int(xml.find('TripStopStatus').text)
    offroute = int(xml.find('TripStopStatus').text)
    if offroute == 2:
        item['messagetype'] = 'OFFROUTE'
    elif tripstatus == 1:
        item['messagetype'] = 'ARRIVAL'
    elif tripstatus == 2:
        item['messagetype'] = 'DEPARTURE'
    elif tripstatus == 3:
        item['messagetype'] = 'ONROUTE'
    elif tripstatus == 4:
        item['messagetype'] = 'DELAY'
    else:
        print tripstatus
        return None
    source = int(xml.find('SourceSystemMessage').text)
    if source == 1:
        item['source'] = 'VEHICLE'
    elif source == 2:
        item['source'] = 'SERVER'
    return item

def kv6tojson(contents):
    xml = ET.fromstring(contents)
    version = xml.find('Version')
    results = []
    if version is not None and version.text == '8.07':
        for dossiers in xml.findall('Dossiers'):
            for dossier in dossiers.findall('Dossier'):
                for dossierobjects in dossier.findall('DossierObjects'):
                    for dossierobject in dossierobjects.findall('DossierObject'):
                        for objectdata in dossierobject.findall('ObjectData'):
                            for rowdata in objectdata.findall('RowData'):
                                item = kv6_807to810(rowdata)
                                if item is None:
                                    print contents
                                else:
                                    results.append(item)
    if xml.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}VV_TM_PUSH':
        posinfo = xml.findall('{http://bison.connekt.nl/tmi8/kv6/msg}KV6posinfo')
        for dossier in posinfo:
            for child in dossier.getchildren():
                if child.tag != '{http://bison.connekt.nl/tmi8/kv6/core}delimiter':
                    result = fetchfrommessage(child)
                    if result is not None:
                        results.append(result)
    return results
