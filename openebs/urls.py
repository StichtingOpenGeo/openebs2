from django.conf.urls import patterns, url
from openebs.views import MessageListView, MessageCreateView, MessageDeleteView, ScenarioListView

urlpatterns = patterns('',
    # Berichten views
    url(r'^$', MessageListView.as_view(), name="msg_index"),
    url(r'^bericht/nieuw$', MessageCreateView.as_view(), name="msg_add"),
    url(r'^bericht/verwijderen/(?P<pk>\d+)$', MessageDeleteView.as_view(), name="msg_delete"),

    # Scenario views
    url(r'^scenario$', ScenarioListView.as_view(), name="scenario_index")
)
