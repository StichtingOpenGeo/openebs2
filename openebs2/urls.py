from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from openebs2 import settings
from utils.views import ErrorView

admin.autodiscover()

# Custom error handlers
handler403 = ErrorView.as_view(template_name="openebs/nopermission.html")
handler404 = ErrorView.as_view(template_name="openebs/notfound.html")
handler500 = ErrorView.as_view(template_name="openebs/servererror.html")

urlpatterns = patterns('',
    url(r'^', include('openebs.urls')),
    url(r'^', include('kv1.urls')),

    url(r'^inloggen/$', 'django.contrib.auth.views.login', {'template_name': 'users/login.html'}, name="app_login"),
    url(r'^uitloggen/$', 'django.contrib.auth.views.logout_then_login', name="app_logout"),
    url(r'^wachtwoord/wijzigen$', 'django.contrib.auth.views.password_change', {'template_name': 'users/password_change_form.html'}, name="app_password_change"),
    url(r'^wachtwoord/gewijzigd$', 'django.contrib.auth.views.password_change_done', {'template_name': 'users/password_change_done.html'}, name="app_password_changed"),
    url(r'^geweigerd/$', TemplateView.as_view(template_name="openebs/templates/openebs/nopermission.html"), name="app_nopermission"),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)