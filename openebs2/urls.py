from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

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
    url(r'^geweigerd/$', TemplateView.as_view(template_name="openebs/nopermission.html"), name="app_nopermission"),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)