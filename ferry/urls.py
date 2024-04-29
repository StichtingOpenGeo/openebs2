from django.urls import re_path

from ferry.views import FerryHomeView, FerryDepartedView, FerryCancelledView, FerrySuspendedView, FerryTripJsonView, \
    FerryRecoveredView, FerryDelayedView, FerryFullView

urlpatterns = [
                   re_path(r'^ferry/departure', FerryDepartedView.as_view(), name="ferry_depart"),
                   re_path(r'^ferry/delay', FerryDelayedView.as_view(), name="ferry_delay"),
                   re_path(r'^ferry/full', FerryFullView.as_view(), name="ferry_full"),
                   re_path(r'^ferry/cancel', FerryCancelledView.as_view(), name="ferry_cancel"),
                   re_path(r'^ferry/suspend', FerrySuspendedView.as_view(), name="ferry_suspend"),
                   re_path(r'^ferry/recover', FerryRecoveredView.as_view(), name="ferry_recover"),
                   re_path(r'^ferry/$', FerryHomeView.as_view(), name="ferry_home"),

                   re_path(r'^ferry/(?P<pk>\w+)/trips.json$', FerryTripJsonView.as_view(), name="ferry_trips_json")
                ]
