from django.urls import re_path
from kv1.views import LineSearchView, LineStopView, ActiveStopListView, LineTripView, DataImportView, \
    ActiveMessagesForStopView, StopAutocompleteView, StopLineSearchView, StopLineFilterView, StopSearchView

urlpatterns = [
    re_path(r'^line/(?P<search>\w+)?$', LineSearchView.as_view(), name="line_search"),
    re_path(r'^line/(?P<pk>\w+)/stops$', LineStopView.as_view(), name="line_show"),
    re_path(r'^line/(?P<pk>\w+)/ritten$', LineTripView.as_view(), name="line_show"),
    re_path(r'^vervoerder/data', DataImportView.as_view(), name="kv1_imports"),

    re_path(r'^haltes.geojson$', ActiveStopListView.as_view(), name="msg_geojson"),
    re_path(r'^stop/(?P<tpc>\w+)/messages.json$', ActiveMessagesForStopView.as_view(), name="msg_stop_json"),
    re_path(r'^stop/search.json$', StopAutocompleteView.as_view(), name="stop_search_json"),

    re_path(r'^stop/lines$', StopLineFilterView.as_view(), name="stopline_search"),
    re_path(r'^stop$', StopSearchView.as_view(), name="stop_search"),
    re_path(r'^stop/(?P<pk>\w+)/lines$', StopLineSearchView.as_view(), name="stopline_search")
]
