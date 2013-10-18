from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.utils.translation import ugettext_lazy as _
from openebs.models import Kv15Stopmessage, UserProfile

admin.site.register(Kv15Stopmessage)

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