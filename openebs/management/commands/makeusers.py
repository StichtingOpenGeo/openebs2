import codecs
import csv

from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand

from openebs.models import UserProfile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('groupname', nargs='+', type=str)

    def handle(self, *args, **options):
        print("Creating users")
        g = Group.objects.get(name=options['groupname'][0])
        with open(options['filename'][0], 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            first = True
            for row in reader:
                if first:
                    first = False
                else:
                    username = row[1].rstrip().lower().replace(' ', '')
                    password = 'WelkomVeolia!'
                    u = User.objects.create_user(username, row[2].lower(), password,
                                                 first_name=row[1].split(' ')[0],
                                                 last_name=' '.join(row[1].split(' ')[1:]))
                    UserProfile(user=u, company="VTN").save()
                    g.user_set.add(u)
                    print("%s;%s;%s" % (username, row[2].lower().rstrip(), password))
