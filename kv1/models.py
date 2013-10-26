from django.contrib.gis.db import models
from json_field import JSONField
from kv15.enum import DATAOWNERCODE
from django.utils.translation import ugettext_lazy as _

class Kv1Line(models.Model):
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    lineplanningnumber = models.CharField(max_length=10)
    publiclinenumber = models.CharField(max_length=10)
    headsign = models.CharField(max_length=100)
    stop_map = JSONField()

    class Meta:
        verbose_name = _("Lijninformatie")
        verbose_name_plural = _("Lijninformatie")
        unique_together = ('dataownercode', 'lineplanningnumber')

    def __unicode__(self):
        return u"%s - %s" % (self.dataownercode, self.headsign)

class Kv1Stop(models.Model):
    userstopcode = models.CharField(max_length=10, unique=True) # TPC
    dataownercode = models.CharField(max_length=10, choices=DATAOWNERCODE)
    name = models.CharField(max_length=50)
    location = models.PointField()

    # Custom manager for geomodels/searches
    objects = models.GeoManager()

    class Meta:
        verbose_name = _("Halteinformatie")
        verbose_name_plural = _("Halteinformatie")

    def __unicode__(self):
        return u"%s - %s" % (self.dataownercode, self.name)


