from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from reports.views import VehicleReportView, VehicleReportDetailsView, LineDetailsView

admin.autodiscover()

# Custom error handlers
handler403 = TemplateView.as_view(template_name="openebs/nopermission.html")
handler404 = TemplateView.as_view(template_name="openebs/notfound.html")
handler500 = TemplateView.as_view(template_name="openebs/servererror.html")


urlpatterns = patterns('',
    url(r'^', include('openebs.urls')),
    url(r'^', include('kv1.urls')),

    url(r'^inloggen/$', 'django.contrib.auth.views.login', {'template_name': 'users/login.html'}, name="app_login"),
    url(r'^uitloggen/$', 'django.contrib.auth.views.logout_then_login', name="app_logout"),
    url(r'^wachtwoord/wijzigen$', 'django.contrib.auth.views.password_change', {'template_name': 'users/password_change_form.html'}, name="app_password_change"),
    url(r'^wachtwoord/gewijzigd$', 'django.contrib.auth.views.password_change_done', {'template_name': 'users/password_change_done.html'}, name="app_password_changed"),
    url(r'^geweigerd/$', TemplateView.as_view(template_name="openebs/nopermission.html"), name="app_nopermission"),

    url(r'^report/lijnen/$', VehicleReportView.as_view(), name="report_vehicles"),
    url(r'^report/lijnen.json$', VehicleReportDetailsView.as_view(), name="report_details"),
    url(r'^report/lijn/(?P<line>\d+).json$', LineDetailsView.as_view(), name="report_line_details"),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
)