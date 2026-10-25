import csv
import os
from django.db import connection, transaction, Error

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
    # Journeys and their dates are too many to do one by one: these columns are copied into a temporary table
    JOURNEY_COLUMNS = ['journey_id', 'base_departure_time', 'direction', 'availabilityconditionref']
    JOURNEY_DATE_COLUMNS = ['privatecode', 'availabilityconditionref', 'validdate']

    def add_arguments(self, parser):
        parser.add_argument('folder', type=str)

    def handle(self, *args, **options):
        self.folder = options.get('folder', '')
        print("STEP 1: Lines")
        self.do_lines()
        print("==========================\n\nSTEP 2: Stops")
        self.do_stops()
        print("==========================\n\nSTEP 3: Journeys")
        self.do_journeys()
        print("==========================\n\nSTEP 4: Journey dates")
        self.do_journey_dates()

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

    def copy_csv(self, cursor, name, table, columns):
        """ Copy the given columns of an export into a temporary table, by name so other columns don't matter """
        csv_file, reader = self.open_csv(name, columns)
        with csv_file:
            # ON COMMIT DROP doesn't happen when we're inside an outer transaction, so make sure it's gone
            cursor.execute("DROP TABLE IF EXISTS %s" % table)
            cursor.execute("CREATE TEMPORARY TABLE %s (%s) ON COMMIT DROP" %
                           (table, ", ".join("%s text" % column for column in columns)))
            cursor.copy_expert("COPY %s FROM STDIN WITH CSV" % table, CsvColumns(reader, columns))
            # Without statistics the planner thinks the table is tiny and loops over it for every line
            cursor.execute("ANALYZE %s" % table)

    def do_journeys(self):
        if not os.path.exists(self.folder + '/openebs_journeys.csv'):
            self.log("No openebs_journeys.csv, skipping journeys")
            return
        try:
            with transaction.atomic(), connection.cursor() as cursor:
                self.copy_csv(cursor, 'openebs_journeys.csv', 'tmp_journeys', self.JOURNEY_COLUMNS)
                # Insert new trips. Note: need to still delete old trips (related to archiving)
                # Journeys with an id we can't parse are skipped rather than failing the whole import
                cursor.execute("""
                    INSERT INTO kv1_kv1journey (dataownercode, line_id, journeynumber, scheduleref, direction, departuretime)
                    SELECT DISTINCT ON (t.dataownercode, l.id, t.journeynumber, t.scheduleref)
                           t.dataownercode, l.id, t.journeynumber, t.scheduleref, t.direction, t.departuretime
                    FROM (
                        SELECT split_part(journey_id, ':', 1) AS dataownercode,
                               split_part(journey_id, ':', 2) AS lineplanningnumber,
                               cast(split_part(journey_id, ':', 3) AS integer) AS journeynumber,
                               cast(availabilityconditionref AS integer) AS scheduleref,
                               cast(direction AS integer) AS direction,
                               cast(base_departure_time AS integer) AS departuretime
                        FROM tmp_journeys
                        WHERE split_part(journey_id, ':', 3) ~ '^[0-9]{1,9}$' AND availabilityconditionref ~ '^[0-9]{1,9}$'
                        AND direction ~ '^[0-9]{1,4}$' AND base_departure_time ~ '^[0-9]{1,9}$'
                    ) t
                    JOIN kv1_kv1line l ON l.dataownercode = t.dataownercode AND l.lineplanningnumber = t.lineplanningnumber
                    WHERE NOT EXISTS (
                        SELECT 1 FROM kv1_kv1journey j WHERE j.dataownercode = t.dataownercode AND j.line_id = l.id
                        AND j.journeynumber = t.journeynumber AND j.scheduleref = t.scheduleref
                    )""")
                self.log("Added %s journeys" % cursor.rowcount)
        except (Error, ValueError) as error:
            self.log("Issue importing journeys: %s" % error)
            self.import_errors += 1

    def do_journey_dates(self):
        if not os.path.exists(self.folder + '/openebs_journey_dates.csv'):
            self.log("No openebs_journey_dates.csv, skipping journey dates")
            return
        try:
            # We don't link to these, so replace them all. In one transaction so a failure keeps the old dates
            with transaction.atomic(), connection.cursor() as cursor:
                self.copy_csv(cursor, 'openebs_journey_dates.csv', 'tmp_journey_dates', self.JOURNEY_DATE_COLUMNS)
                cursor.execute("DELETE FROM kv1_kv1journeydate")
                # Match on the parts of the id, so the unique index on journeys can be used
                cursor.execute("""
                    INSERT INTO kv1_kv1journeydate (journey_id, date)
                    SELECT DISTINCT j.id, t.date
                    FROM (
                        SELECT split_part(privatecode, ':', 1) AS dataownercode,
                               split_part(privatecode, ':', 2) AS lineplanningnumber,
                               cast(split_part(privatecode, ':', 3) AS integer) AS journeynumber,
                               cast(availabilityconditionref AS integer) AS scheduleref,
                               cast(validdate AS date) AS date
                        FROM tmp_journey_dates
                        WHERE split_part(privatecode, ':', 3) ~ '^[0-9]{1,9}$' AND availabilityconditionref ~ '^[0-9]{1,9}$'
                        AND validdate ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                    ) t
                    JOIN kv1_kv1line l ON l.dataownercode = t.dataownercode AND l.lineplanningnumber = t.lineplanningnumber
                    JOIN kv1_kv1journey j ON j.dataownercode = t.dataownercode AND j.line_id = l.id
                    AND j.journeynumber = t.journeynumber AND j.scheduleref = t.scheduleref""")
                self.log("Added %s journey dates" % cursor.rowcount)
        except (Error, ValueError) as error:
            self.log("Issue importing journey dates: %s" % error)
            self.import_errors += 1

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


class CsvColumns(object):
    """
    File-like object for COPY: the given columns of each row of a DictReader, as CSV. Streams, so a large export
    doesn't have to fit in memory
    """
    def __init__(self, reader, columns):
        self.rows = ([row[column] for column in columns] for row in reader)
        self.buffer = ''

    def read(self, size=-1):
        while size < 0 or len(self.buffer) < size:
            try:
                row = next(self.rows)
            except StopIteration:
                break
            self.buffer += ",".join(self.quote(value) for value in row) + "\n"
        if size < 0:
            size = len(self.buffer)
        data, self.buffer = self.buffer[:size], self.buffer[size:]
        return data

    @staticmethod
    def quote(value):
        if value is None or value == '':
            return ''
        return '"%s"' % value.replace('"', '""')
