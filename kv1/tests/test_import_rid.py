from datetime import time
from django.utils.unittest.case import TestCase
from kv1.management.commands.import_rid import Command as ImportCommand
from kv1.models import Kv1Line, Kv1Stop, Kv1Journey


class TestRidImporter(TestCase):

    @classmethod
    def setUpClass(self):
        self.testClass = ImportCommand()
        self.testClass.folder = "/tmp/"


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
        print list(Kv1Stop.objects.filter())
        print l_a.stop_map
        # Data
        lines = [
            ['operator_id','publiccode','name'],
            ['VTN:1049','62','Gulpen - Vaals'],
        ]
        stops = [
            ['operator_id','name','longitude','latitude'],
            ['VTN:15023014','Busstation Perron C', '1', '2'] # Load an updated name
        ]
        self.createTestFile('lines.csv', lines)
        self.createTestFile('stops.csv', stops)
        self.createTestFile('journey_stops.csv', [])
        self.createTestFile('journey_dates.csv', [])

        self.testClass.handle('/tmp')

        line = Kv1Line.objects.get(dataownercode='VTN', lineplanningnumber=1049)
        self.assertEqual(Kv1Line.objects.count(), num_lines)
        self.assertEqual(line.publiclinenumber, lines[1][1])
        self.assertEqual(line.headsign, lines[1][2])

        print list(Kv1Stop.objects.filter())
        self.assertEqual(Kv1Stop.objects.count(), num_stops+1)
        stop = Kv1Stop.objects.filter(dataownercode=15023014, userstopcode='15023014')[0]
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

    def createTestFile(self, name, data):
        with open('/tmp/'+name, 'w') as outfile:
            outfile.write("\r\n".join([",".join(line) for line in data]))