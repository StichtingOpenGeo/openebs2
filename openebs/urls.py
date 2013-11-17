from django.conf.urls import patterns, url
from django.views.generic import RedirectView, TemplateView
# from djgeojson.views import GeoJSONLayerView
from djgeojson.views import GeoJSONLayerView
from openebs.views import MessageListView, MessageCreateView, MessageDeleteView, ScenarioListView, ScenarioCreateView, ScenarioMessageCreateView, ScenarioUpdateView, ScenarioMessageDeleteView, ScenarioDeleteView, MessageUpdateView, ScenarioMessageUpdateView, PlanScenarioView, ScenarioStopsAjaxView, ActiveStopsAjaxView

urlpatterns = patterns('',
    # Onze Index
    url(r'^$', RedirectView.as_view(url='/bericht')),

    # Kaart views
    url(r'^kaart$', TemplateView.as_view(template_name='openebs/kv15stopmessage_map.html'), name="msg_map"),

    # Berichten views
    url(r'^bericht$', MessageListView.as_view(), name="msg_index"),
    url(r'^bericht/nieuw$', MessageCreateView.as_view(), name="msg_add"),
    url(r'^bericht/(?P<pk>\d+)/bewerken$', MessageUpdateView.as_view(), name="msg_edit"),
    url(r'^bericht/(?P<pk>\d+)/verwijderen$', MessageDeleteView.as_view(), name="msg_delete"),
    url(r'^bericht/haltes.json', ActiveStopsAjaxView.as_view(), name="scenario_stops_ajax"),

    # Scenario views
    url(r'^scenario$', ScenarioListView.as_view(), name="scenario_index"),
    url(r'^scenario/nieuw$', ScenarioCreateView.as_view(), name="scenario_add"),
    url(r'^scenario/(?P<pk>\d+)/bewerk', ScenarioUpdateView.as_view(), name="scenario_edit"),
    url(r'^scenario/(?P<pk>\d+)/verwijderen', ScenarioDeleteView.as_view(), name="scenario_delete"),
    url(r'^scenario/(?P<scenario>\d+)/inplannen', PlanScenarioView.as_view(), name="scenario_plan"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/nieuw$', ScenarioMessageCreateView.as_view(), name="scenario_msg_add"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/bewerken', ScenarioMessageUpdateView.as_view(), name="scenario_msg_edit"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/verwijderen', ScenarioMessageDeleteView.as_view(), name="scenario_msg_delete"),
    url(r'^scenario/(?P<scenario>\d+)/haltes.geojson', ScenarioStopsAjaxView.as_view(), name="scenario_stops_ajax"),

)
