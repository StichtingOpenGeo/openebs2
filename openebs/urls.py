from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from openebs.views import MessageListView, MessageCreateView, MessageDeleteView, ScenarioListView, ScenarioCreateView, ScenarioMessageCreateView, ScenarioUpdateView, ScenarioMessageDeleteView, ScenarioDeleteView, MessageUpdateView

urlpatterns = patterns('',
    # Onze Index
    url(r'^$', RedirectView.as_view(url='/bericht')),

    # Berichten views
    url(r'^bericht$', MessageListView.as_view(), name="msg_index"),
    url(r'^bericht/nieuw$', MessageCreateView.as_view(), name="msg_add"),
    url(r'^bericht/(?P<pk>\d+)/bewerken$', MessageUpdateView.as_view(), name="msg_edit"),
    url(r'^bericht/(?P<pk>\d+)/verwijderen$', MessageDeleteView.as_view(), name="msg_delete"),

    # Scenario views
    url(r'^scenario$', ScenarioListView.as_view(), name="scenario_index"),
    url(r'^scenario/nieuw$', ScenarioCreateView.as_view(), name="scenario_add"),
    url(r'^scenario/(?P<pk>\d+)/bewerk', ScenarioUpdateView.as_view(), name="scenario_edit"),
    url(r'^scenario/(?P<pk>\d+)/delete', ScenarioDeleteView.as_view(), name="scenario_delete"),
    url(r'^scenario/(?P<pk>\d+)/bericht/nieuw$', ScenarioMessageCreateView.as_view(), name="scenario_msg_add"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/verwijderen', ScenarioMessageDeleteView.as_view(), name="scenario_msg_delete"),

)
