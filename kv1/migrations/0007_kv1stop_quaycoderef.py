# Generated by Django 4.2.11 on 2024-07-18 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kv1', '0006_auto_20230406_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='kv1stop',
            name='quaycoderef',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]