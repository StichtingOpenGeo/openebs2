from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from openebs2 import settings
from django.contrib.auth import views as auth_views


admin.autodiscover()

# Custom error handlers
handler403 = TemplateView.as_view(template_name="openebs/nopermission.html")
handler404 = TemplateView.as_view(template_name="openebs/notfound.html")
handler500 = TemplateView.as_view(template_name="openebs/servererror.html")

urlpatterns = [
    url(r'^', include('openebs.urls')),
    url(r'^', include('kv1.urls')),
    url(r'^', include('ferry.urls')),

    url(r'^inloggen/$', auth_views.login, {'template_name': 'users/login.html'}, name="app_login"),
    url(r'^uitloggen/$', auth_views.logout_then_login, name="app_logout"),
    url(r'^wachtwoord/wijzigen$', auth_views.password_change, {'template_name': 'users/password_change_form.html'}, name="app_password_change"),
    url(r'^wachtwoord/gewijzigd$', auth_views.password_change_done, {'template_name': 'users/password_change_done.html'}, name="password_change_done"),
    url(r'^geweigerd/$', TemplateView.as_view(template_name="openebs/nopermission.html"), name="app_nopermission"),

    url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)