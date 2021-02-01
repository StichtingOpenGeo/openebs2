from os import listdir
from os.path import isfile, join, splitext, split

from django.core.management import BaseCommand

from kv1.models import Kv1Line


class Command(BaseCommand):
    args = '<directory>'
    help = 'Step 1 of import: imports line and stop order from json files'

    def handle(self, *args, **options):
        self.parse_directory(args[0])

    def parse_directory(self, directory):
        for filename in self.get_files(directory):
            self.parse_line(filename)

    @staticmethod
    def get_files(dir):
        return [join(dir, f) for f in listdir(dir) if isfile(join(dir, f)) and splitext(join(dir, f))[1] == ".json"]

    @staticmethod
    def parse_line(filename):
        # Determine operator and planning number
        line_split = splitext(split(filename)[1])[0].split('_')
        qry = Kv1Line.objects.filter(dataownercode=line_split[0], lineplanningnumber=line_split[1])
        if qry.count() == 1:
            line = qry[0]
        else:
            line = Kv1Line()
            line.dataownercode = line_split[0]
            line.lineplanningnumber = line_split[1]

        # Parse file
        with open(filename, 'r') as input:
            # TODO add more checks
            line.stop_map = input.read()
        line.save()
