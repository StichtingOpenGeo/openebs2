from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from kv1.models import Kv1Line, Kv1Stop

admin.site.register(Kv1Line) # Temporary

class StopAdmin(OSMGeoAdmin):
    model = Kv1Stop
    default_zoom = 30

admin.site.register(Kv1Stop, StopAdmin) # Temporary