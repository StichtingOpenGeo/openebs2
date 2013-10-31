from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.utils.translation import ugettext_lazy as _
from openebs.models import Kv15Stopmessage, Kv15Log, Kv15Scenario, UserProfile, Kv15StopmessageUserstopcode


class MessageStopInline(admin.StackedInline):
    model = Kv15StopmessageUserstopcode
    verbose_name_plural = _("haltes")
    extra = 1

class Kv15MessageAdmin(admin.ModelAdmin):
    model = Kv15Stopmessage
    inlines = (MessageStopInline, )

admin.site.register(Kv15Stopmessage, Kv15MessageAdmin)
admin.site.register(Kv15Scenario)
admin.site.register(Kv15Log)

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("profiel")

class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Remove this
admin.site.unregister(Site)
