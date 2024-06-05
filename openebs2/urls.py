from django.conf.urls import include
from django.urls import path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from openebs2 import settings
from django.contrib.auth import views as auth_views

from utils.views import handler403, handler404, handler500

admin.autodiscover()

# Custom error handlers
handler403 = handler403
handler404 = handler404
handler500 = handler500

urlpatterns = [
    re_path(r'^', include('openebs.urls')),
    re_path(r'^', include('kv1.urls')),
    re_path(r'^', include('ferry.urls')),

    re_path(r'^inloggen/$', auth_views.LoginView.as_view(template_name='users/login.html'), name="app_login"),
    re_path(r'^uitloggen/$', auth_views.logout_then_login, name="app_logout"),
    re_path(r'^wachtwoord/wijzigen$', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'), name="app_password_change"),
    re_path(r'^wachtwoord/gewijzigd$', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name="password_change_done"),
    re_path(r'^geweigerd/$', TemplateView.as_view(template_name="openebs/nopermission.html"), name="app_nopermission"),

    path('admin/', admin.site.urls),
    path("accounts/", include('allauth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
