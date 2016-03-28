
from django.contrib import admin
from django.db.models import ForeignKey
from django_admin_bootstrapped.widgets import GenericContentTypeSelect

from ferry.models import FerryKv6Messages, FerryLine


class FerryLineAdmin(admin.ModelAdmin):
    list_display = ('line', 'stop_depart', 'stop_arrival')
    raw_id_fields = ('line', 'stop_depart', 'stop_arrival', 'scenario_cancelled')

admin.site.register(FerryKv6Messages)
admin.site.register(FerryLine, FerryLineAdmin)