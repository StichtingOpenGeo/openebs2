from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from kv1.models import Kv1Line, Kv1Stop


class LineAdmin(admin.ModelAdmin):
    model=Kv1Line
    list_display = ('lineplanningnumber', 'headsign', 'dataownercode')
    list_filter = ('dataownercode', )

admin.site.register(Kv1Line, LineAdmin) # Temporary

class StopAdmin(OSMGeoAdmin):
    model = Kv1Stop
    list_display = ('name', 'userstopcode', 'dataownercode')
    list_filter = ('dataownercode', )
    default_zoom = 30

admin.site.register(Kv1Stop, StopAdmin) # Temporary