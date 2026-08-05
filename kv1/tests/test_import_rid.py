
import csv
import tempfile

from django.contrib.gis.geos import Point
from django.core.management import call_command, CommandError
from django.test import TestCase

from kv1.management.commands.import_rid import Command as ImportCommand
from kv1.models import Kv1Line, Kv1Stop, Kv1Journey, ImportStatus


class TestRidImporter(TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    #def testLinesSimple(self):
    #    # Setup model
    #    l_a, created = Kv1Line.objects.get_or_create(dataownercode='VTN', lineplanningnumber=1048, defaults= { 'stop_map' : '{}' })
    #
    #    self.assertEqual(Kv1Line.objects.count(), 1)
    #
    #    # Data
    #    lines = [
    #        ['operator_id','publiccode','name'],
    #        ['VTN:1048','61','Gulpen - Vaals via Vijlen']
    #    ]
    #    self.createTestFile('lines.csv', lines)
    #    self.createTestFile('stops.csv', [])
    #    self.createTestFile('journey_stops.csv', [])
    #    self.createTestFile('journey_dates.csv', [])
    #
    #    self.testClass.handle('/tmp')
    #
    #    line = Kv1Line.objects.get(dataownercode='VTN', lineplanningnumber=1048)
    #    self.assertEqual(Kv1Line.objects.count(), 1)
    #    self.assertEqual(line.publiclinenumber, lines[1][1])
    #    self.assertEqual(line.headsign, lines[1][2])

    def testStopsSimple(self):
        # Setup model
        map = '[{"right": {"id": "VTN_15023014", "name": "Geleen, Busstation Perron C"}, "left": {"id": "VTN_15023014", "name": "Geleen, Busstation Perron C"}}]'
        l_a, created = Kv1Line.objects.get_or_create(dataownercode='VTN', lineplanningnumber=1049, defaults= { 'stop_map' : '{}' })
        l_a.stop_map = map
        l_a.save()

        num_lines = Kv1Line.objects.count()
        num_stops = Kv1Stop.objects.count()

        # Data
        lines = [
            ['bison_id','publiccode','name'],
            ['VTN:1049','62','Gulpen - Vaals'],
        ]
        stops = [
            ['operator_id','name','longitude','latitude','timingpointcode','quaycoderef'],
            ['VTN:15023014','Busstation Perron C', '1', '2','15023014','NL:Q:15023014']  # Load an updated name
        ]
        self.createTestFile('openebs_lines.csv', lines)
        self.createTestFile('openebs_stops.csv', stops)

        call_command('import_rid', self.folder.name)

        line = Kv1Line.objects.get(dataownercode='VTN', lineplanningnumber=1049)
        self.assertEqual(Kv1Line.objects.count(), num_lines)
        self.assertEqual(line.publiclinenumber, lines[1][1])
        self.assertEqual(line.headsign, lines[1][2])

        self.assertEqual(Kv1Stop.objects.count(), num_stops+1)
        stop = Kv1Stop.objects.filter(dataownercode='VTN', userstopcode='15023014')[0]
        self.assertEqual(stop.name, stops[1][1])
        self.assertEqual(stop.location.x, float(stops[1][2]))
        self.assertEqual(stop.location.y, float(stops[1][3]))

    #def testJourneyStopsDatesSimple(self):
    #    map = '[{"right": {"id": "VTN_15023010", "name": "Geleen, Busstation Perron A"}, "left": {"id": "VTN_15023010", "name": "Geleen, Busstation Perron A"}}]'
    #    l_a, created = Kv1Line.objects.get_or_create(dataownercode='VTN', lineplanningnumber=1048, stop_map=map)
    #
    #    # Data
    #    lines = [
    #        ['operator_id','publiccode','name'],
    #        ['VTN:1048','61','Gulpen - Vaals'],
    #    ]
    #    stops = [
    #        ['operator_id','name','longitude','latitude'],
    #        ['VTN:15023010','Busstation Perron A', '1', '2'] # Load an updated name
    #    ]
    #    journey_stops = [
    #        ['journey_id','stop_sequence','userstopcode','arrival_time','departure_time','timepoint'],
    #        ['VTN:1048:1', '1', 'VTN:15023010','59760','59880','f']
    #    ]
    #    journey_dates = [
    #        ['privatecode', 'validdate'],
    #        ['VTN:1048:1', '2013-12-01'],
    #        ['VTN:1048:1', '2013-12-02'],
    #        ['VTN:1048:1', '2013-12-03']
    #    ]
    #    self.createTestFile('lines.csv', lines)
    #    self.createTestFile('stops.csv', stops)
    #    self.createTestFile('journey_stops.csv', journey_stops)
    #    self.createTestFile('journey_dates.csv', journey_dates)
    #
    #    self.testClass.handle('/tmp')
    #
    #    self.assertEqual(Kv1Journey.objects.count(), 1)
    #    journey = Kv1Journey.objects.filter()[0]
    #    self.assertEqual(journey.dataownercode, 'VTN')
    #    self.assertEqual(journey.line.lineplanningnumber, '1048')
    #    self.assertEqual(journey.journeynumber, 1)
    #    self.assertEqual(journey.dates.count(), 3)
    #    self.assertEqual([o.date.isoformat() for o in journey.dates.filter()],
    #                     ['2013-12-01', '2013-12-02', '2013-12-03'])
    #    self.assertEqual(journey.stops.count(), 1)
    #    self.assertEqual(journey.stops.filter()[0].stop.dataownercode, 'VTN')
    #    self.assertEqual(journey.stops.filter()[0].stop.userstopcode, '15023010')
    #    self.assertEqual(journey.stops.filter()[0].stoporder, 1)
    #    self.assertEqual(journey.stops.filter()[0].targetarrival, time(17, 36))
    #    self.assertEqual(journey.stops.filter()[0].targetdeparture, time(17, 38))

    def testRefs(self):
        Kv1Line.objects.create(dataownercode='HTM', lineplanningnumber='1', stop_map='{}')
        self.createTestFile('openebs_lines.csv', [
            ['bison_id', 'publiccode', 'name', 'original_ref'],
            ['HTM:1', '1', 'Scheveningen - Delft', 'NL:HTM:Line:1'],
        ])
        self.createTestFile('openebs_stops.csv', [
            ['operator_id', 'name', 'latitude', 'longitude', 'timingpointcode', 'quaycoderef', 'original_ref'],
            ['HTM:9006', 'Delft, Noordeinde', '52.016435', '4.351544', '9006', 'NL:Q:32009006',
             'NL:HTM:ScheduledStopPoint:R9006'],
            ['GVB:07494', 'Emplacement Zuid', '52.33866', '4.863729', '07494', '', ''],
        ])
        call_command('import_rid', self.folder.name)

        self.assertEqual('NL:HTM:Line:1', Kv1Line.objects.get(dataownercode='HTM').original_ref)
        stop = Kv1Stop.objects.get(dataownercode='HTM', userstopcode='9006')
        self.assertEqual('NL:Q:32009006', stop.quaycoderef)
        self.assertEqual('NL:HTM:ScheduledStopPoint:R9006', stop.original_ref)
        stop = Kv1Stop.objects.get(dataownercode='GVB', userstopcode='07494')
        self.assertIsNone(stop.quaycoderef)
        self.assertIsNone(stop.original_ref)

    def testUnknownColumns(self):
        """ New columns in the export are ignored, wherever they are """
        Kv1Line.objects.create(dataownercode='HTM', lineplanningnumber='1', stop_map='{}')
        self.createTestFile('openebs_lines.csv', [
            ['transportmode', 'bison_id', 'publiccode', 'name', 'brand'],
            ['TRAM', 'HTM:1', '1', 'Scheveningen - Delft', 'HTM'],
        ])
        self.createTestFile('openebs_stops.csv', [
            ['tariff_zones', 'operator_id', 'name', 'latitude', 'longitude', 'timingpointcode', 'quaycoderef',
             'platformcode'],
            ['{NL:DOVA:TariffZone:5426}', 'HTM:9006', 'Delft, Noordeinde', '52.016435', '4.351544', '9006',
             'NL:Q:32009006', 'A'],
        ])
        call_command('import_rid', self.folder.name)

        self.assertEqual('Scheveningen - Delft', Kv1Line.objects.get(dataownercode='HTM').headsign)
        self.assertEqual('NL:Q:32009006', Kv1Stop.objects.get(dataownercode='HTM', userstopcode='9006').quaycoderef)

    def testOlderExportKeepsRefs(self):
        """ An export without the optional columns doesn't wipe what we already have """
        Kv1Line.objects.create(dataownercode='HTM', lineplanningnumber='1', stop_map='{}', original_ref='NL:HTM:Line:1')
        Kv1Stop.objects.create(dataownercode='HTM', userstopcode='9006', name='Oud', location=Point(1, 1),
                               quaycoderef='NL:Q:32009006', original_ref='NL:HTM:ScheduledStopPoint:R9006')
        self.createTestFile('openebs_lines.csv', [['bison_id', 'publiccode', 'name'], ['HTM:1', '1', 'Lijn 1']])
        self.createTestFile('openebs_stops.csv', [
            ['operator_id', 'name', 'latitude', 'longitude'],
            ['HTM:9006', 'Delft, Noordeinde', '52.016435', '4.351544'],
        ])
        call_command('import_rid', self.folder.name)

        self.assertEqual('NL:HTM:Line:1', Kv1Line.objects.get(dataownercode='HTM').original_ref)
        stop = Kv1Stop.objects.get(dataownercode='HTM', userstopcode='9006')
        self.assertEqual('Delft, Noordeinde', stop.name)
        self.assertEqual('NL:Q:32009006', stop.quaycoderef)
        self.assertEqual('NL:HTM:ScheduledStopPoint:R9006', stop.original_ref)

    def testMissingRequiredColumn(self):
        self.createTestFile('openebs_lines.csv', [['bison_id', 'publiccode', 'name']])
        self.createTestFile('openebs_stops.csv', [['operator_id', 'name', 'latitude']])
        with self.assertRaisesRegex(CommandError, 'openebs_stops.csv is missing column\\(s\\) longitude'):
            call_command('import_rid', self.folder.name)

    def testBadRowIsSkipped(self):
        self.createTestFile('openebs_lines.csv', [['bison_id', 'publiccode', 'name']])
        self.createTestFile('openebs_stops.csv', [
            ['operator_id', 'name', 'latitude', 'longitude'],
            ['HTM:9005', 'Kapot', 'onbekend', '4.351226'],
            ['NOCOLON', 'Geen code', '52.0', '4.3'],
            ['HTM:9006', 'Delft, Noordeinde', '52.016435', '4.351544'],
        ])
        call_command('import_rid', self.folder.name)

        self.assertEqual(['9006'], list(Kv1Stop.objects.values_list('userstopcode', flat=True)))
        self.assertEqual("Er waren 2 fouten.", ImportStatus.objects.latest('importDate').status)

    def createTestFile(self, name, data):
        with open(self.folder.name + '/' + name, 'w', newline='') as outfile:
            csv.writer(outfile).writerows(data)