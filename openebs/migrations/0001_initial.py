# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import openebs.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kv1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kv15Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('dataownercode', models.CharField(max_length=10, verbose_name='Vervoerder', choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('messagecodedate', models.DateField()),
                ('messagecodenumber', models.IntegerField()),
                ('message', models.CharField(max_length=255)),
                ('ipaddress', models.CharField(max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Logbericht',
                'verbose_name_plural': 'Logberichten',
                'permissions': (('view_log', 'Logberichten inzien'),),
            },
        ),
        migrations.CreateModel(
            name='Kv15MessageLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('line', models.ForeignKey(to='kv1.Kv1Line', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Kv15MessageStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stop', models.ForeignKey(related_name='messages', to='kv1.Kv1Stop', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Kv15Scenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Naam scenario', blank=True)),
                ('dataownercode', models.CharField(max_length=10, verbose_name='Vervoerder', choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('description', models.CharField(max_length=255, verbose_name='Omschrijving scenario', blank=True)),
            ],
            options={
                'verbose_name': 'Scenario',
                'verbose_name_plural': "Scenario's",
                'permissions': (('view_scenario', "Scenario's bekijken"), ('add_scenario', "Scenario's aanmaken")),
            },
        ),
        migrations.CreateModel(
            name='Kv15ScenarioMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dataownercode', models.CharField(max_length=10, verbose_name='Vervoerder', choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('messagepriority', models.CharField(default='PTPROCESS', max_length=10, verbose_name='Prioriteit', choices=[(b'CALAMITY', b'Calamiteit'), (b'PTPROCESS', b'OV'), (b'COMMERCIAL', b'Commercieel'), (b'MISC', b'Overig')])),
                ('messagetype', models.CharField(default='GENERAL', max_length=10, verbose_name='Type bericht', choices=[(b'GENERAL', b'Algemeen'), (b'ADDITIONAL', b'Extra'), (b'OVERRULE', b'Overschrijf'), (b'BOTTOMLINE', b'Onderaan')])),
                ('messagedurationtype', models.CharField(default='ENDTIME', max_length=10, verbose_name='Type tijdsrooster', choices=[(b'REMOVE', b'Verwijder'), (b'FIRSTVEJO', b'Volgende rit'), (b'ENDTIME', b'Eind Tijd')])),
                ('messagecontent', models.CharField(max_length=255, verbose_name='Bericht', blank=True)),
                ('reasontype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type oorzaak', choices=[(0, b'Onbekend'), (1, b'Overig'), (2, b'Personeel'), (3, b'Materieel'), (4, b'Omgeving'), (255, b'Ongedefinieerd')])),
                ('subreasontype', models.CharField(blank=True, max_length=10, verbose_name='Oorzaak', choices=[(b'0_1', b'Eerdere verstoring'), (b'11', b'Herstel werkzaamheden'), (b'11_2', b'Uitloop herstelwerkzaamheden'), (b'12', b'Stroomstoring'), (b'12_1', b'Defecte bovenleiding'), (b'12_2', b'Uitloop werkzaamheden'), (b'14', b'Defecte brug'), (b'14', b'Wateroverlast'), (b'14_1', b'Defect viaduct'), (b'15', b'File'), (b'16', b'Route versperd'), (b'16', b'Stremming'), (b'17', b'Mensen op de route'), (b'18', b'Auto in spoor'), (b'19_1', b'Omgevallen bomen'), (b'20', b'Vee op de route'), (b'23', b'Werkzaamheden'), (b'23_1', b'Rioleringswerkzaamheden'), (b'23_2', b'Wegwerkzaamheden'), (b'23_3', b'Asfalteringswerkzaamheden'), (b'23_4', b'Bestratingswerkzaamheden'), (b'24_1', b'Optocht'), (b'24_10', b'Kermis'), (b'24_11', b'Koniginnedag'), (b'24_12', b'Marathon'), (b'24_13', b'Wielerronde'), (b'24_14', b'Voetbalwedstrijd'), (b'24_15', b'Herdenking'), (b'24_16', b'Avondvierdaagse'), (b'24_6', b'Bloemencorso'), (b'24_7', b'Braderie'), (b'24_8', b'Carnaval'), (b'24_9', b'Jaarmarkt'), (b'255', b'Onbekend'), (b'255', b'Weersomstandigheden'), (b'255_1', b'Blikeminslag'), (b'26_1', b'Snelheidsbeperkingen'), (b'26_2', b'Logistieke problemen'), (b'3', b'Sneeuw'), (b'3_1', b'Op last van de politie'), (b'3_11', b'Ontruiming'), (b'3_15', b'Ruimen WO II bom'), (b'3_17', b'Op last van de brandweer'), (b'3_9', b'Bommelding'), (b'4', b'Brand'), (b'4', b'Seinstoring'), (b'4', b'Tekort aan personeel'), (b'4_1', b'Sein en wisselstoring'), (b'5', b'Ontsporing'), (b'5', b'Staking'), (b'5', b'Storm'), (b'5', b'Vakbondsacties'), (b'5_1', b'Mogelijke staking'), (b'6', b'Ongeval'), (b'6', b'Stiptheidsactie'), (b'6_2', b'Defecte trein'), (b'6_3', b'Aanrijding met een persoon'), (b'6_4', b'Passagier onwel'), (b'6_6', b'Aanrijding'), (b'7', b'Defect materieel'), (b'7', b'Extreme drukte'), (b'8_1', b'Defect spoor'), (b'8_10', b'Wisselstoring'), (b'8_11', b'Overwegstoring'), (b'8_12', b'Storing in verkeersleidingsysteem'), (b'8_13', b'Gladde sporen'), (b'8_4', b'Tekort aan materieel'), (b'9', b'Herstelwerkzaamheden'), (b'9_1', b'Gladheid'), (b'9_2', b'IJsgang'), (b'9_2', b'IJzel')])),
                ('reasoncontent', models.CharField(max_length=255, verbose_name='Uitleg oorzaak', blank=True)),
                ('effecttype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type gevolg', choices=[(0, b'Onbekend'), (1, b'Algemeen Effect'), (255, b'Ongedefineerd')])),
                ('subeffecttype', models.CharField(blank=True, max_length=10, verbose_name='Gevolg', choices=[(b'0', b'onbekend'), (b'11', b'minder vervoer'), (b'5', b'geen vervoer'), (b'6', b'vervoer ontregeld'), (b'5', b'geen treinen'), (b'4', b'omleiding'), (b'4_1', b'omleiding met vertraging'), (b'3_1', b'vertraging onbekend'), (b'3_2', b'vertraging 5 min.'), (b'3_3', b'vertraging 10 min.'), (b'3_4', b'vertraging 15 min.'), (b'3_5', b'vertraging 30 min.'), (b'3_6', b'vertraging 45 min.'), (b'3_7', b'vertraging 60 min.'), (b'3_8', b'vertraging 60 min. en meer'), (b'3_9', b'vertraging 5 tot 10 min.'), (b'3_10', b'vertraging 10 tot 15 min.'), (b'3_11', b'vertraging 15 tot 30 min.'), (b'3_12', b'vertraging 30 tot 60 min.'), (b'5_1', b'vervallen halte(n)'), (b'5_2', b'traject vervallen')])),
                ('effectcontent', models.CharField(max_length=255, verbose_name='Uitleg gevolg', blank=True)),
                ('measuretype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type aanpassing', choices=[(0, b'Onbekend'), (1, b'Algemene Maatregel'), (255, b'Ongedefineerd')])),
                ('submeasuretype', models.CharField(blank=True, max_length=10, verbose_name='Aanpassing', choices=[(b'0', b'extra vervoer'), (b'1', b'vervallen halte(n)'), (b'2', b'vervangende halte(n)'), (b'3', b'rijden via omweg'), (b'4_1', b'geen businzet'), (b'4_2', b'beperkte businzet'), (b'4_3', b'businzet'), (b'5_1', b'geen treinen'), (b'5_2', b'minder treinen'), (b'5_3', b'treinen rijden via'), (b'6', b'geen'), (b'7', b'route aangepast')])),
                ('measurecontent', models.CharField(max_length=255, verbose_name='Uitleg aanpassing', blank=True)),
                ('advicetype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type advies', choices=[(0, b'Onbekend'), (1, b'Algemeen Advies'), (255, b'Ongedefineerd')])),
                ('subadvicetype', models.CharField(blank=True, max_length=10, verbose_name='Advies', choices=[(b'0', b'geen'), (b'1', b'niet reizen'), (b'2', b'reizen met ander ov'), (b'3_1', b'overstappen in'), (b'3_2', b'reizen via'), (b'3_3', b'in-/uitstappen')])),
                ('advicecontent', models.CharField(max_length=255, verbose_name='Uitleg advies', blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('scenario', models.ForeignKey(related_name='messages', to='openebs.Kv15Scenario', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Scenario bericht',
                'verbose_name_plural': 'Scenario berichten',
            },
        ),
        migrations.CreateModel(
            name='Kv15ScenarioStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.ForeignKey(related_name='stops', to='openebs.Kv15ScenarioMessage', on_delete=models.CASCADE)),
                ('stop', models.ForeignKey(to='kv1.Kv1Stop', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Kv15Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('messagestarttime', models.DateTimeField(null=True, blank=True)),
                ('messageendtime', models.DateTimeField(null=True, blank=True)),
                ('weekdays', models.SmallIntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Kv15Stopmessage',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('dataownercode', models.CharField(max_length=10, verbose_name='Vervoerder', choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('messagecodedate', models.DateField(default=django.utils.timezone.now, verbose_name='Datum')),
                ('messagecodenumber', models.IntegerField(verbose_name='Volgnummer')),
                ('messagepriority', models.CharField(default='PTPROCESS', max_length=10, verbose_name='Prioriteit', choices=[(b'CALAMITY', b'Calamiteit'), (b'PTPROCESS', b'OV'), (b'COMMERCIAL', b'Commercieel'), (b'MISC', b'Overig')])),
                ('messagetype', models.CharField(default='GENERAL', max_length=10, verbose_name='Type bericht', choices=[(b'GENERAL', b'Algemeen'), (b'ADDITIONAL', b'Extra'), (b'OVERRULE', b'Overschrijf'), (b'BOTTOMLINE', b'Onderaan')])),
                ('messagedurationtype', models.CharField(default='ENDTIME', max_length=10, verbose_name='Type tijdsrooster', choices=[(b'REMOVE', b'Verwijder'), (b'FIRSTVEJO', b'Volgende rit'), (b'ENDTIME', b'Eind Tijd')])),
                ('messagestarttime', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Begintijd', blank=True)),
                ('messageendtime', models.DateTimeField(default=openebs.models.get_end_service, null=True, verbose_name='Eindtijd', blank=True)),
                ('messagecontent', models.CharField(max_length=255, null=True, verbose_name='Bericht', blank=True)),
                ('reasontype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type oorzaak', choices=[(0, b'Onbekend'), (1, b'Overig'), (2, b'Personeel'), (3, b'Materieel'), (4, b'Omgeving'), (255, b'Ongedefinieerd')])),
                ('subreasontype', models.CharField(blank=True, max_length=10, verbose_name='Oorzaak', choices=[(b'0_1', b'Eerdere verstoring'), (b'11', b'Herstel werkzaamheden'), (b'11_2', b'Uitloop herstelwerkzaamheden'), (b'12', b'Stroomstoring'), (b'12_1', b'Defecte bovenleiding'), (b'12_2', b'Uitloop werkzaamheden'), (b'14', b'Defecte brug'), (b'14', b'Wateroverlast'), (b'14_1', b'Defect viaduct'), (b'15', b'File'), (b'16', b'Route versperd'), (b'16', b'Stremming'), (b'17', b'Mensen op de route'), (b'18', b'Auto in spoor'), (b'19_1', b'Omgevallen bomen'), (b'20', b'Vee op de route'), (b'23', b'Werkzaamheden'), (b'23_1', b'Rioleringswerkzaamheden'), (b'23_2', b'Wegwerkzaamheden'), (b'23_3', b'Asfalteringswerkzaamheden'), (b'23_4', b'Bestratingswerkzaamheden'), (b'24_1', b'Optocht'), (b'24_10', b'Kermis'), (b'24_11', b'Koniginnedag'), (b'24_12', b'Marathon'), (b'24_13', b'Wielerronde'), (b'24_14', b'Voetbalwedstrijd'), (b'24_15', b'Herdenking'), (b'24_16', b'Avondvierdaagse'), (b'24_6', b'Bloemencorso'), (b'24_7', b'Braderie'), (b'24_8', b'Carnaval'), (b'24_9', b'Jaarmarkt'), (b'255', b'Onbekend'), (b'255', b'Weersomstandigheden'), (b'255_1', b'Blikeminslag'), (b'26_1', b'Snelheidsbeperkingen'), (b'26_2', b'Logistieke problemen'), (b'3', b'Sneeuw'), (b'3_1', b'Op last van de politie'), (b'3_11', b'Ontruiming'), (b'3_15', b'Ruimen WO II bom'), (b'3_17', b'Op last van de brandweer'), (b'3_9', b'Bommelding'), (b'4', b'Brand'), (b'4', b'Seinstoring'), (b'4', b'Tekort aan personeel'), (b'4_1', b'Sein en wisselstoring'), (b'5', b'Ontsporing'), (b'5', b'Staking'), (b'5', b'Storm'), (b'5', b'Vakbondsacties'), (b'5_1', b'Mogelijke staking'), (b'6', b'Ongeval'), (b'6', b'Stiptheidsactie'), (b'6_2', b'Defecte trein'), (b'6_3', b'Aanrijding met een persoon'), (b'6_4', b'Passagier onwel'), (b'6_6', b'Aanrijding'), (b'7', b'Defect materieel'), (b'7', b'Extreme drukte'), (b'8_1', b'Defect spoor'), (b'8_10', b'Wisselstoring'), (b'8_11', b'Overwegstoring'), (b'8_12', b'Storing in verkeersleidingsysteem'), (b'8_13', b'Gladde sporen'), (b'8_4', b'Tekort aan materieel'), (b'9', b'Herstelwerkzaamheden'), (b'9_1', b'Gladheid'), (b'9_2', b'IJsgang'), (b'9_2', b'IJzel')])),
                ('reasoncontent', models.CharField(max_length=255, verbose_name='Uitleg oorzaak', blank=True)),
                ('effecttype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type gevolg', choices=[(0, b'Onbekend'), (1, b'Algemeen Effect'), (255, b'Ongedefineerd')])),
                ('subeffecttype', models.CharField(blank=True, max_length=10, verbose_name='Gevolg', choices=[(b'0', b'onbekend'), (b'11', b'minder vervoer'), (b'5', b'geen vervoer'), (b'6', b'vervoer ontregeld'), (b'5', b'geen treinen'), (b'4', b'omleiding'), (b'4_1', b'omleiding met vertraging'), (b'3_1', b'vertraging onbekend'), (b'3_2', b'vertraging 5 min.'), (b'3_3', b'vertraging 10 min.'), (b'3_4', b'vertraging 15 min.'), (b'3_5', b'vertraging 30 min.'), (b'3_6', b'vertraging 45 min.'), (b'3_7', b'vertraging 60 min.'), (b'3_8', b'vertraging 60 min. en meer'), (b'3_9', b'vertraging 5 tot 10 min.'), (b'3_10', b'vertraging 10 tot 15 min.'), (b'3_11', b'vertraging 15 tot 30 min.'), (b'3_12', b'vertraging 30 tot 60 min.'), (b'5_1', b'vervallen halte(n)'), (b'5_2', b'traject vervallen')])),
                ('effectcontent', models.CharField(max_length=255, verbose_name='Uitleg gevolg', blank=True)),
                ('measuretype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type aanpassing', choices=[(0, b'Onbekend'), (1, b'Algemene Maatregel'), (255, b'Ongedefineerd')])),
                ('submeasuretype', models.CharField(blank=True, max_length=10, verbose_name='Aanpassing', choices=[(b'0', b'extra vervoer'), (b'1', b'vervallen halte(n)'), (b'2', b'vervangende halte(n)'), (b'3', b'rijden via omweg'), (b'4_1', b'geen businzet'), (b'4_2', b'beperkte businzet'), (b'4_3', b'businzet'), (b'5_1', b'geen treinen'), (b'5_2', b'minder treinen'), (b'5_3', b'treinen rijden via'), (b'6', b'geen'), (b'7', b'route aangepast')])),
                ('measurecontent', models.CharField(max_length=255, verbose_name='Uitleg aanpassing', blank=True)),
                ('advicetype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type advies', choices=[(0, b'Onbekend'), (1, b'Algemeen Advies'), (255, b'Ongedefineerd')])),
                ('subadvicetype', models.CharField(blank=True, max_length=10, verbose_name='Advies', choices=[(b'0', b'geen'), (b'1', b'niet reizen'), (b'2', b'reizen met ander ov'), (b'3_1', b'overstappen in'), (b'3_2', b'reizen via'), (b'3_3', b'in-/uitstappen')])),
                ('advicecontent', models.CharField(max_length=255, verbose_name='Uitleg advies', blank=True)),
                ('messagetimestamp', models.DateTimeField(auto_now_add=True)),
                ('isdeleted', models.BooleanField(default=False, verbose_name='Verwijderd?')),
                ('status', models.SmallIntegerField(default=0, verbose_name='Status', choices=[(0, 'Opgeslagen'), (1, 'Verstuurd'), (2, 'Teruggemeld'), (5, 'Verwijderd'), (6, 'Verwijdering verstuurd'), (7, 'Verwijdering teruggemeld'), (11, 'Fout bij versturen'), (12, 'Fout bij versturen verwijdering')])),
                ('stops', models.ManyToManyField(to='kv1.Kv1Stop', through='openebs.Kv15MessageStop')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'KV15 Bericht',
                'verbose_name_plural': 'KV15 Berichten',
                'permissions': (('view_messages', 'Berichten bekijken'), ('add_messages', 'Berichten toevoegen, aanpassen of verwijderen'), ('view_all', 'Alle berichten inzien'), ('edit_all', 'Alle berichten bewerken')),
            },
        ),
        migrations.CreateModel(
            name='Kv17Change',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dataownercode', models.CharField(max_length=10, verbose_name='Vervoerder', choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('operatingday', models.DateField(verbose_name='Datum')),
                ('reinforcement', models.IntegerField(default=0, verbose_name='Versterkingsnummer')),
                ('is_recovered', models.BooleanField(default=False, verbose_name='Teruggedraaid?')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('recovered', models.DateTimeField(null=True, blank=True)),
                ('journey', models.ForeignKey(related_name='changes', verbose_name='Rit', to='kv1.Kv1Journey', on_delete=models.CASCADE)),
                ('line', models.ForeignKey(verbose_name='Lijn', to='kv1.Kv1Line', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Ritaanpassing',
                'verbose_name_plural': 'Ritaanpassingen',
                'permissions': (('view_change', 'Ritaanpassingen bekijken'), ('add_change', 'Ritaanpassingen aanmaken')),
            },
        ),
        migrations.CreateModel(
            name='Kv17JourneyChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reasontype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type oorzaak', choices=[(0, b'Onbekend'), (1, b'Overig'), (2, b'Personeel'), (3, b'Materieel'), (4, b'Omgeving'), (255, b'Ongedefinieerd')])),
                ('subreasontype', models.CharField(blank=True, max_length=10, verbose_name='Oorzaak', choices=[(b'0_1', b'Eerdere verstoring'), (b'11', b'Herstel werkzaamheden'), (b'11_2', b'Uitloop herstelwerkzaamheden'), (b'12', b'Stroomstoring'), (b'12_1', b'Defecte bovenleiding'), (b'12_2', b'Uitloop werkzaamheden'), (b'14', b'Defecte brug'), (b'14', b'Wateroverlast'), (b'14_1', b'Defect viaduct'), (b'15', b'File'), (b'16', b'Route versperd'), (b'16', b'Stremming'), (b'17', b'Mensen op de route'), (b'18', b'Auto in spoor'), (b'19_1', b'Omgevallen bomen'), (b'20', b'Vee op de route'), (b'23', b'Werkzaamheden'), (b'23_1', b'Rioleringswerkzaamheden'), (b'23_2', b'Wegwerkzaamheden'), (b'23_3', b'Asfalteringswerkzaamheden'), (b'23_4', b'Bestratingswerkzaamheden'), (b'24_1', b'Optocht'), (b'24_10', b'Kermis'), (b'24_11', b'Koniginnedag'), (b'24_12', b'Marathon'), (b'24_13', b'Wielerronde'), (b'24_14', b'Voetbalwedstrijd'), (b'24_15', b'Herdenking'), (b'24_16', b'Avondvierdaagse'), (b'24_6', b'Bloemencorso'), (b'24_7', b'Braderie'), (b'24_8', b'Carnaval'), (b'24_9', b'Jaarmarkt'), (b'255', b'Onbekend'), (b'255', b'Weersomstandigheden'), (b'255_1', b'Blikeminslag'), (b'26_1', b'Snelheidsbeperkingen'), (b'26_2', b'Logistieke problemen'), (b'3', b'Sneeuw'), (b'3_1', b'Op last van de politie'), (b'3_11', b'Ontruiming'), (b'3_15', b'Ruimen WO II bom'), (b'3_17', b'Op last van de brandweer'), (b'3_9', b'Bommelding'), (b'4', b'Brand'), (b'4', b'Seinstoring'), (b'4', b'Tekort aan personeel'), (b'4_1', b'Sein en wisselstoring'), (b'5', b'Ontsporing'), (b'5', b'Staking'), (b'5', b'Storm'), (b'5', b'Vakbondsacties'), (b'5_1', b'Mogelijke staking'), (b'6', b'Ongeval'), (b'6', b'Stiptheidsactie'), (b'6_2', b'Defecte trein'), (b'6_3', b'Aanrijding met een persoon'), (b'6_4', b'Passagier onwel'), (b'6_6', b'Aanrijding'), (b'7', b'Defect materieel'), (b'7', b'Extreme drukte'), (b'8_1', b'Defect spoor'), (b'8_10', b'Wisselstoring'), (b'8_11', b'Overwegstoring'), (b'8_12', b'Storing in verkeersleidingsysteem'), (b'8_13', b'Gladde sporen'), (b'8_4', b'Tekort aan materieel'), (b'9', b'Herstelwerkzaamheden'), (b'9_1', b'Gladheid'), (b'9_2', b'IJsgang'), (b'9_2', b'IJzel')])),
                ('reasoncontent', models.CharField(max_length=255, verbose_name='Uitleg oorzaak', blank=True)),
                ('advicetype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type advies', choices=[(0, b'Onbekend'), (1, b'Algemeen Advies'), (255, b'Ongedefineerd')])),
                ('subadvicetype', models.CharField(blank=True, max_length=10, verbose_name='Advies', choices=[(b'0', b'geen'), (b'1', b'niet reizen'), (b'2', b'reizen met ander ov'), (b'3_1', b'overstappen in'), (b'3_2', b'reizen via'), (b'3_3', b'in-/uitstappen')])),
                ('advicecontent', models.CharField(max_length=255, verbose_name='Uitleg advies', blank=True)),
                ('change', models.ForeignKey(related_name='journey_details', to='openebs.Kv17Change', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Ritaanpassingsdetails',
                'verbose_name_plural': 'Ritaanpassingendetails',
            },
        ),
        migrations.CreateModel(
            name='Kv17StopChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'SHORTEN'), (2, 'LAG'), (3, 'CHANGEPASSTIMES'), (4, 'CHANGEDESTINATION'), (5, 'MUTATIONMESSAGE')])),
                ('stoporder', models.IntegerField()),
                ('lag', models.IntegerField()),
                ('targetarrival', models.DateTimeField()),
                ('targetdeparture', models.DateTimeField()),
                ('stoptype', models.CharField(default='INTERMEDIATE', max_length=12, choices=[(b'FIRST', b'Beginhalte'), (b'INTERMEDIATE', b'Tussenhalte'), (b'LAST', b'Eindhalte')])),
                ('destinationcode', models.CharField(max_length=10, blank=True)),
                ('destinationname50', models.CharField(max_length=50, blank=True)),
                ('destinationname16', models.CharField(max_length=16, blank=True)),
                ('destinationdetail16', models.CharField(max_length=16, blank=True)),
                ('destinationdisplay16', models.CharField(max_length=16, blank=True)),
                ('reasontype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type oorzaak', choices=[(0, b'Onbekend'), (1, b'Overig'), (2, b'Personeel'), (3, b'Materieel'), (4, b'Omgeving'), (255, b'Ongedefinieerd')])),
                ('subreasontype', models.CharField(blank=True, max_length=10, verbose_name='Oorzaak', choices=[(b'0_1', b'Eerdere verstoring'), (b'11', b'Herstel werkzaamheden'), (b'11_2', b'Uitloop herstelwerkzaamheden'), (b'12', b'Stroomstoring'), (b'12_1', b'Defecte bovenleiding'), (b'12_2', b'Uitloop werkzaamheden'), (b'14', b'Defecte brug'), (b'14', b'Wateroverlast'), (b'14_1', b'Defect viaduct'), (b'15', b'File'), (b'16', b'Route versperd'), (b'16', b'Stremming'), (b'17', b'Mensen op de route'), (b'18', b'Auto in spoor'), (b'19_1', b'Omgevallen bomen'), (b'20', b'Vee op de route'), (b'23', b'Werkzaamheden'), (b'23_1', b'Rioleringswerkzaamheden'), (b'23_2', b'Wegwerkzaamheden'), (b'23_3', b'Asfalteringswerkzaamheden'), (b'23_4', b'Bestratingswerkzaamheden'), (b'24_1', b'Optocht'), (b'24_10', b'Kermis'), (b'24_11', b'Koniginnedag'), (b'24_12', b'Marathon'), (b'24_13', b'Wielerronde'), (b'24_14', b'Voetbalwedstrijd'), (b'24_15', b'Herdenking'), (b'24_16', b'Avondvierdaagse'), (b'24_6', b'Bloemencorso'), (b'24_7', b'Braderie'), (b'24_8', b'Carnaval'), (b'24_9', b'Jaarmarkt'), (b'255', b'Onbekend'), (b'255', b'Weersomstandigheden'), (b'255_1', b'Blikeminslag'), (b'26_1', b'Snelheidsbeperkingen'), (b'26_2', b'Logistieke problemen'), (b'3', b'Sneeuw'), (b'3_1', b'Op last van de politie'), (b'3_11', b'Ontruiming'), (b'3_15', b'Ruimen WO II bom'), (b'3_17', b'Op last van de brandweer'), (b'3_9', b'Bommelding'), (b'4', b'Brand'), (b'4', b'Seinstoring'), (b'4', b'Tekort aan personeel'), (b'4_1', b'Sein en wisselstoring'), (b'5', b'Ontsporing'), (b'5', b'Staking'), (b'5', b'Storm'), (b'5', b'Vakbondsacties'), (b'5_1', b'Mogelijke staking'), (b'6', b'Ongeval'), (b'6', b'Stiptheidsactie'), (b'6_2', b'Defecte trein'), (b'6_3', b'Aanrijding met een persoon'), (b'6_4', b'Passagier onwel'), (b'6_6', b'Aanrijding'), (b'7', b'Defect materieel'), (b'7', b'Extreme drukte'), (b'8_1', b'Defect spoor'), (b'8_10', b'Wisselstoring'), (b'8_11', b'Overwegstoring'), (b'8_12', b'Storing in verkeersleidingsysteem'), (b'8_13', b'Gladde sporen'), (b'8_4', b'Tekort aan materieel'), (b'9', b'Herstelwerkzaamheden'), (b'9_1', b'Gladheid'), (b'9_2', b'IJsgang'), (b'9_2', b'IJzel')])),
                ('reasoncontent', models.CharField(max_length=255, verbose_name='Uitleg oorzaak', blank=True)),
                ('advicetype', models.SmallIntegerField(blank=True, null=True, verbose_name='Type advies', choices=[(0, b'Onbekend'), (1, b'Algemeen Advies'), (255, b'Ongedefineerd')])),
                ('subadvicetype', models.CharField(blank=True, max_length=10, verbose_name='Advies', choices=[(b'0', b'geen'), (b'1', b'niet reizen'), (b'2', b'reizen met ander ov'), (b'3_1', b'overstappen in'), (b'3_2', b'reizen via'), (b'3_3', b'in-/uitstappen')])),
                ('advicecontent', models.CharField(max_length=255, verbose_name='Uitleg advies', blank=True)),
                ('change', models.ForeignKey(to='openebs.Kv17Change', on_delete=models.CASCADE)),
                ('stop', models.ForeignKey(to='kv1.Kv1Stop', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Halteaanpassing',
                'verbose_name_plural': 'Halteaanpassingen',
            },
        ),
        migrations.CreateModel(
            name='Kv1StopFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('description', models.TextField(max_length=200, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Filter',
                'verbose_name_plural': 'Filters',
            },
        ),
        migrations.CreateModel(
            name='Kv1StopFilterStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filter', models.ForeignKey(related_name='stops', to='openebs.Kv1StopFilter', on_delete=models.CASCADE)),
                ('stop', models.ForeignKey(to='kv1.Kv1Stop', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(max_length=10, verbose_name='Vervoerder', choices=[(b'ARR', b'Arriva'), (b'VTN', b'Veolia'), (b'CXX', b'Connexxion'), (b'EBS', b'EBS'), (b'GVB', b'GVB'), (b'HTM', b'HTM'), (b'NS', b'Nederlandse Spoorwegen'), (b'RET', b'RET'), (b'SYNTUS', b'Syntus'), (b'QBUZZ', b'Qbuzz'), (b'TCR', b'Taxi Centrale Renesse'), (b'GOVI', b'GOVI')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='kv15schedule',
            name='stopmessage',
            field=models.ForeignKey(to='openebs.Kv15Stopmessage', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='kv15messagestop',
            name='stopmessage',
            field=models.ForeignKey(to='openebs.Kv15Stopmessage', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='kv15messageline',
            name='stopmessage',
            field=models.ForeignKey(to='openebs.Kv15Stopmessage', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='kv17change',
            unique_together=set([('operatingday', 'line', 'journey', 'reinforcement')]),
        ),
        migrations.AlterUniqueTogether(
            name='kv15stopmessage',
            unique_together=set([('dataownercode', 'messagecodedate', 'messagecodenumber')]),
        ),
        migrations.AlterUniqueTogether(
            name='kv15messagestop',
            unique_together=set([('stopmessage', 'stop')]),
        ),
        migrations.AlterUniqueTogether(
            name='kv15messageline',
            unique_together=set([('stopmessage', 'line')]),
        ),
    ]
