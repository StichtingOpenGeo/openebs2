from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from kv1.models import *


class LineAdmin(admin.ModelAdmin):
    model = Kv1Line
    list_display = ('lineplanningnumber', 'headsign', 'dataownercode')
    list_filter = ('dataownercode', )

admin.site.register(Kv1Line, LineAdmin)


class StopAdmin(OSMGeoAdmin):
    model = Kv1Stop
    list_display = ('name', 'userstopcode', 'dataownercode')
    list_filter = ('dataownercode', )
    default_zoom = 30

admin.site.register(Kv1Stop, StopAdmin)


class JourneyStopInline(admin.TabularInline):
    model = Kv1Journey.journeystops.through

class JourneyDatesInline(admin.TabularInline):
    model = Kv1JourneyDate
    extra = 1

class JourneyAdmin(admin.ModelAdmin):
    model = Kv1Journey
    list_display = ('dataownercode', 'line', 'journeynumber', )
    list_filter = ('dataownercode', )
    inlines = [JourneyDatesInline]
    #exclude = ('journeystops', )
admin.site.register(Kv1Journey, JourneyAdmin)