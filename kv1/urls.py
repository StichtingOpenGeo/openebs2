from django.conf.urls import patterns, url
from kv1.views import LineSearchView, LineStopView, ActiveStopListView, LineTripView, DataImportView

urlpatterns = patterns('',
                        url(r'^line/(?P<search>\w+)?$', LineSearchView.as_view(), name="line_search"),
                        url(r'^line/(?P<pk>\w+)/stops$', LineStopView.as_view(), name="line_show"),
                        url(r'^line/(?P<pk>\w+)/ritten$', LineTripView.as_view(), name="line_show"),
                        url(r'^haltes.geojson$', ActiveStopListView.as_view(), name="msg_geojson"),

                        url(r'^vervoerder/data', DataImportView.as_view(), name="kv1_imports")
                       )