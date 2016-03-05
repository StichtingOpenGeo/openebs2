from django.conf.urls import patterns, url

from ferry.views import FerryHomeView, FerryDepartedView, FerryCancelledView, FerrySuspendedView, FerryTripJsonView, \
    FerryRecoveredView, FerryDelayedView, FerryFullView

urlpatterns = patterns('',
                       url(r'^ferry/departure', FerryDepartedView.as_view(), name="ferry_depart"),
                       url(r'^ferry/delay', FerryDelayedView.as_view(), name="ferry_delay"),
                       url(r'^ferry/full', FerryFullView.as_view(), name="ferry_full"),
                       url(r'^ferry/cancel', FerryCancelledView.as_view(), name="ferry_cancel"),
                       url(r'^ferry/suspend', FerrySuspendedView.as_view(), name="ferry_suspend"),
                       url(r'^ferry/recover', FerryRecoveredView.as_view(), name="ferry_recover"),
                       url(r'^ferry/$', FerryHomeView.as_view(), name="ferry_home"),

                       url(r'^ferry/(?P<pk>\w+)/trips.json$', FerryTripJsonView.as_view(), name="ferry_trips_json")
                       )