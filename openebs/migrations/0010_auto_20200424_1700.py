# Generated by Django 2.2.9 on 2020-04-24 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openebs', '0009_kv17changeline_monitoring_error'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kv17changeline',
            name='monitoring_error',
            field=models.CharField(choices=[('GPS', 'Storing in de GPS van het voertuig'), ('GPRS', 'Storing in het mobiele netwerk'), ('Radio', 'Storing in de radioverbinding'), ('General', 'Voertuigsysteem werkt niet'), ('NoSystem', 'Voertuig heeft geen volgapparatuur'), ('other', 'Andere oorzaak'), ('unknown', 'Onbekende oorzaak')], default=False, max_length=40, null=True, verbose_name='Monitoring_error'),
        ),
    ]
