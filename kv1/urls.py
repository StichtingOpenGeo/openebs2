from django.conf.urls import patterns, url
from kv1.views import LineSearchView, LineShowView

urlpatterns = patterns('',
                        url(r'^line/(?P<search>\w+)?$', LineSearchView.as_view(), name="line_search"),
                        url(r'^line/(?P<pk>\w+)/stops$', LineShowView.as_view(), name="line_show"),

                       )