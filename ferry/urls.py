from django.conf.urls import patterns, url

from ferry.views import FerryHomeView

urlpatterns = patterns('',
                       url(r'^ferry/', FerryHomeView.as_view(), name="ferry_home"),
                       )