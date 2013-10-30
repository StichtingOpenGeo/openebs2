import re, json
from os import listdir
from os.path import isfile, join, splitext, split
from django.core.management import BaseCommand
from kv1.models import Kv1Line

class Command(BaseCommand):
    REGEX_BASE = 'id=\"'+'([A-Z]{3,10}_[0-9]{3,10})' + '">' + '(.*?)' + '</'
    REGEX_EMPTY = '<td></td>'

    args = '<directory>'
    help = 'Step 1 of import: imports line and stop data from html files'

    re_left_right = re.compile(REGEX_BASE+'.*'+REGEX_BASE)
    re_left = re.compile(REGEX_BASE+'.*'+REGEX_EMPTY)
    re_right = re.compile(REGEX_EMPTY+'.*'+REGEX_BASE)

    def handle(self, *args, **options):
        self.parse_directory(args[0])

    def parse_directory(self, dir):
        for filename in self.get_files(dir):
            self.parse_line(filename)

    def get_files(self, dir):
        return [ join(dir,f) for f in listdir(dir) if isfile(join(dir,f)) and splitext(join(dir,f))[1] == ".html" ]

    def parse_line(self, filename):
        # Determine operator and planning number
        line_split = splitext(split(filename)[1])[0].split('_')
        qry = Kv1Line.objects.filter(dataownercode=line_split[0], lineplanningnumber=line_split[1])
        if qry.count() == 1:
            l = qry[0]
        else:
            l = Kv1Line()
            l.dataownercode = line_split[0]
            l.lineplanningnumber = line_split[1]

        # Parse file
        with open(filename, 'r') as input:
            l.stop_map = self.parse_file(input)
        l.save()

    def parse_file(self, file):
        output = []
        i = 0
        errors = 0
        contents = file.readlines()

        for line in contents:
            i += 1
            m = self.re_left_right.search(line)
            if m:
                output.append({'left' : {'id': m.group(1), 'name': m.group(2)}, 'right': {'id': m.group(3), 'name': m.group(4)}})
                continue

            m_left = self.re_left.search(line)
            if m_left:
                output.append({'left' : {'id': m_left.group(1), 'name': m_left.group(2)}, 'right' : None})
                continue

            m_right = self.re_right.search(line)
            if m_right:
                output.append({'left': None, 'right' : {'id': m_right.group(1), 'name': m_right.group(2)}})
                continue

            errors += 1

        if errors > 1:
            print "Failed on file %s (%s x)" % (file.name, errors)

        return json.dumps(output)