from django.conf.urls import patterns, url

from ferry.views import FerryHomeView, FerryDepartedView, FerryCancelledView, FerrySuspendedView

urlpatterns = patterns('',
                       url(r'^ferry/departure', FerryDepartedView.as_view(), name="ferry_depart"),
                       url(r'^ferry/cancel', FerryCancelledView.as_view(), name="ferry_cancel"),
                       url(r'^ferry/suspend', FerrySuspendedView.as_view(), name="ferry_suspend"),
                       #url(r'^ferry/recover', FerryCancelledView.as_view(), name="ferry_recover"),
                       url(r'^ferry/$', FerryHomeView.as_view(), name="ferry_home"),
                       )