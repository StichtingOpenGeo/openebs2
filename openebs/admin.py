from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Permission, Group
from django.contrib.sites.models import Site
from django.forms import forms

from django.utils.translation import ugettext_lazy as _
from openebs.models import Kv15Stopmessage, Kv15Log, Kv15Scenario, UserProfile, Kv15MessageStop, Kv15ScenarioMessage


class MessageStopInline(admin.StackedInline):
    model = Kv15MessageStop
    verbose_name_plural = _("haltes")
    extra = 1

class Kv15MessageAdmin(admin.ModelAdmin):
    model = Kv15Stopmessage
    inlines = (MessageStopInline, )

admin.site.register(Kv15Stopmessage, Kv15MessageAdmin)

class ScenarioMessageInline(admin.StackedInline):
    model = Kv15ScenarioMessage
    verbose_name = _("bericht")
    verbose_name_plural = _("berichten")
    extra = 0

class Kv15ScenarioAdmin(admin.ModelAdmin):
    model = Kv15Scenario
    inlines = (ScenarioMessageInline, )

admin.site.register(Kv15Scenario, Kv15ScenarioAdmin)
admin.site.register(Kv15Log)

class PermissionFilterMixin(object):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ('permissions', 'user_permissions'):
            qs = kwargs.get('queryset', db_field.rel.to.objects)
            if not request.user.is_superuser: # This hides all the other permissions if we're "just" staff
                qs = qs.exclude(name__startswith="Can")
            kwargs['queryset'] = qs

        return super(PermissionFilterMixin, self).formfield_for_manytomany(db_field, request, **kwargs)

class MyGroupAdmin(PermissionFilterMixin, GroupAdmin):
    pass

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("profiel")

class UserAdmin(PermissionFilterMixin, UserAdmin):
    inlines = (ProfileInline, )

# Re-register Group and User Admins
admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Remove this
admin.site.unregister(Site)
