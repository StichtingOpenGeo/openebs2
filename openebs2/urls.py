from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from reports.views import VehicleReportView, ActiveVehiclesListView, GraphDataView

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
    url(r'^report/lijnen/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/journeys.json$', GraphDataView.as_view(report_type='journeys'), name="ajax_graph_journeys"),
    url(r'^report/lijnen/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/vehicles.json$', GraphDataView.as_view(report_type='vehicles'), name="ajax_graph_vehicles"),
    url(r'^report/lijnen/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/week/journeys.json$', GraphDataView.as_view(report_type='journeys', period='week'), name="ajax_graph_journeys_week"),
    url(r'^report/lijnen/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/week/vehicles.json$', GraphDataView.as_view(report_type='vehicles', period='week'), name="ajax_graph_vehicles_week"),
    url(r'^report/lijnen/live.json$', ActiveVehiclesListView.as_view(), name="ajax_vehicles"),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
)