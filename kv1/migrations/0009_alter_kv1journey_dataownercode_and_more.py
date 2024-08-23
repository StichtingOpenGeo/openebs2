# Generated by Django 4.2.11 on 2024-08-23 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kv1', '0008_alter_kv1journey_dataownercode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kv1journey',
            name='dataownercode',
            field=models.CharField(choices=[('ARR', 'Arriva'), ('VTN', 'Veolia'), ('CXX', 'Connexxion'), ('EBS', 'EBS'), ('GVB', 'GVB'), ('HTM', 'HTM'), ('NS', 'Nederlandse Spoorwegen'), ('RET', 'RET'), ('SYNTUS', 'Syntus'), ('KEOLIS', 'Keolis'), ('QBUZZ', 'Qbuzz'), ('TCR', 'Taxi Centrale Renesse'), ('GOVI', 'GOVI'), ('WSF', 'Westerschelde Ferry'), ('ZTM', 'Gemeente Zoetermeer'), ('TESO', 'TESO'), ('DOEKSEN', 'Rederij Doeksen'), ('WPD', 'Wagenborg Passagiersdiensten')], max_length=10),
        ),
        migrations.AlterField(
            model_name='kv1line',
            name='dataownercode',
            field=models.CharField(choices=[('ARR', 'Arriva'), ('VTN', 'Veolia'), ('CXX', 'Connexxion'), ('EBS', 'EBS'), ('GVB', 'GVB'), ('HTM', 'HTM'), ('NS', 'Nederlandse Spoorwegen'), ('RET', 'RET'), ('SYNTUS', 'Syntus'), ('KEOLIS', 'Keolis'), ('QBUZZ', 'Qbuzz'), ('TCR', 'Taxi Centrale Renesse'), ('GOVI', 'GOVI'), ('WSF', 'Westerschelde Ferry'), ('ZTM', 'Gemeente Zoetermeer'), ('TESO', 'TESO'), ('DOEKSEN', 'Rederij Doeksen'), ('WPD', 'Wagenborg Passagiersdiensten')], max_length=10),
        ),
        migrations.AlterField(
            model_name='kv1stop',
            name='dataownercode',
            field=models.CharField(choices=[('ARR', 'Arriva'), ('VTN', 'Veolia'), ('CXX', 'Connexxion'), ('EBS', 'EBS'), ('GVB', 'GVB'), ('HTM', 'HTM'), ('NS', 'Nederlandse Spoorwegen'), ('RET', 'RET'), ('SYNTUS', 'Syntus'), ('KEOLIS', 'Keolis'), ('QBUZZ', 'Qbuzz'), ('TCR', 'Taxi Centrale Renesse'), ('GOVI', 'GOVI'), ('WSF', 'Westerschelde Ferry'), ('ZTM', 'Gemeente Zoetermeer'), ('TESO', 'TESO'), ('DOEKSEN', 'Rederij Doeksen'), ('WPD', 'Wagenborg Passagiersdiensten')], max_length=10),
        ),
    ]
