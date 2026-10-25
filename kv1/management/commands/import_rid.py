import csv
from django.db import connection, Error

# Hack to disable logging for now
# TODO: test if we can remove this
connection.use_debug_cursor = False

from django.contrib.gis.geos import Point
from django.core.management import BaseCommand, CommandError
from django.utils.datetime_safe import datetime
from kv1.models import Kv1Line, Kv1Stop, ImportStatus
from django.utils.timezone import make_aware


class Command(BaseCommand):
    """
    Import data exports from the RID database
    """
    folder = ""

    # Columns we can't do without, anything else in the export is optional and unknown columns are ignored
    LINE_COLUMNS = ['bison_id']
    STOP_COLUMNS = ['operator_id', 'name', 'latitude', 'longitude']
    # Optional CSV column -> model field. Only updated if the column is in the export, so an older export
    # doesn't wipe what a newer one imported
    LINE_FIELDS = {'publiccode': 'publiclinenumber', 'name': 'headsign', 'original_ref': 'original_ref'}
    STOP_FIELDS = {'timingpointcode': 'timingpointcode', 'quaycoderef': 'quaycoderef', 'original_ref': 'original_ref'}
    NULLABLE_FIELDS = {'quaycoderef', 'original_ref'}  # Store an empty value as NULL

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str)

    def handle(self, *args, **options):
        self.folder = options.get('folder', '')
        print("STEP 1: Lines")
        self.do_lines()
        print("==========================\n\nSTEP 2: Stops")
        self.do_stops()

        self.get_status()

        # hier schrijven we in het model ImportStatus
        ImportStatus.objects.create(importDate=make_aware(datetime.now()), status=self.import_status)

    def open_csv(self, name, required):
        """ Open an export, checking it has the columns we need """
        csv_file = open(self.folder + '/' + name, newline='')
        reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        missing = [column for column in required if column not in (reader.fieldnames or [])]
        if missing:
            csv_file.close()
            raise CommandError("%s is missing column(s) %s, got %s" % (name, ', '.join(missing), reader.fieldnames))
        return csv_file, reader

    @classmethod
    def update_fields(cls, obj, row, fields):
        for column, field in fields.items():
            if column not in row:
                continue
            value = row[column]
            if field in cls.NULLABLE_FIELDS and value == '':
                value = None
            setattr(obj, field, value)

    def do_lines(self):
        routes_file, routes_reader = self.open_csv('openebs_lines.csv', self.LINE_COLUMNS)
        with routes_file:
            for row in routes_reader:
                try:
                    self.do_line(row)
                except (Error, ValueError) as error:
                    self.log("Issue parsing line: %s (with row: %s)" % (error, row))
                    self.import_errors += 1

    def do_line(self, row):
        linenumber = row['bison_id'].split(':')
        if len(linenumber) < 2:
            self.log("Failed to match route: %s" % row)
            return

        lines = Kv1Line.objects.filter(dataownercode=linenumber[0], lineplanningnumber=linenumber[1])
        if lines.count() == 1:
            line = lines[0]
            self.update_fields(line, row, self.LINE_FIELDS)
            line.save()
        else:
            self.log("Failed to match route: %s" % row['bison_id'])

    def do_stops(self):
        stops_file, stop_reader = self.open_csv('openebs_stops.csv', self.STOP_COLUMNS)
        with stops_file:
            i = 0
            for row in stop_reader:
                try:
                    self.do_stop(row)
                    i += 1
                    if i % 100 == 0:
                        self.log("Did %s stops" % i)
                except (Error, ValueError) as error:
                    self.log("Issue parsing stop: %s (with row: %s)" % (error, row))
                    self.import_errors += 1

    def do_stop(self, row):
        stop_code = row['operator_id'].split(':')
        if len(stop_code) < 2:
            raise ValueError("Can't find dataowner and userstopcode in %s" % row['operator_id'])
        location = Point(float(row['longitude']), float(row['latitude']), srid=4326)
        s, created = Kv1Stop.objects.get_or_create(dataownercode=stop_code[0], userstopcode=stop_code[1],
                                                   defaults={'location': location})
        s.name = row['name']
        s.location = location
        self.update_fields(s, row, self.STOP_FIELDS)
        s.save()

    def log(self, text):
        self.stdout.write("%s - import_rid: %s" % (datetime.now().isoformat(), text))

    def get_status(self):
        if self.import_errors == 0:
            self.import_status = "Succesvol"
        elif self.import_errors == 1:
            self.import_status = "Er was " + str(self.import_errors) + " fout."
        else:
            self.import_status = "Er waren " + str(self.import_errors) + " fouten."

    def __init__(self):
        super().__init__()
        self.import_errors = 0
        self.import_status = ""
