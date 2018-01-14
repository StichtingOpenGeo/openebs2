from django.conf.urls import url
from django.views.generic import RedirectView
from openebs.views import MessageListView, MessageCreateView, MessageDeleteView, MessageUpdateView, ActiveStopsAjaxView, MessageDetailsView, MessageStopsAjaxView, \
    MessageStopsBoundAjaxView, MessageResendView
from openebs.views_change import ChangeListView, ChangeCreateView, ChangeDeleteView, ActiveJourneysAjaxView, ChangeUpdateView
from openebs.views_filters import FilterListView, FilterDeleteView, FilterUpdateView, FilterCreateView, \
    FilterStopCreateView, FilterStopDeleteView
from openebs.views_generic import ChangeCompanyView, TemplateRequestView
from openebs.views_scenario import ScenarioListView, ScenarioCreateView, ScenarioUpdateView, ScenarioDeleteView, PlanScenarioView, ScenarioStopsAjaxView
from openebs.views_scenario_msg import ScenarioMessageCreateView, ScenarioMessageUpdateView, ScenarioMessageDeleteView


urlpatterns = [
    # Onze Index
    url(r'^$', RedirectView.as_view(url='/bericht', permanent=True), name='index'),

    # Kaart views
    url(r'^kaart$', TemplateRequestView.as_view(template_name='openebs/kv15stopmessage_map.html'), name="msg_map"),

    # Berichten views
    url(r'^bericht$', MessageListView.as_view(), name="msg_index"),
    url(r'^bericht/nieuw$', MessageCreateView.as_view(), name="msg_add"),
    url(r'^bericht/(?P<pk>\d+)/bekijken', MessageDetailsView.as_view(), name="msg_view"),
    url(r'^bericht/(?P<pk>\d+)/bewerken$', MessageUpdateView.as_view(), name="msg_edit"),
    url(r'^bericht/(?P<pk>\d+)/herhaal', MessageResendView.as_view(), name="msg_resend"),
    url(r'^bericht/(?P<pk>\d+)/verwijderen$', MessageDeleteView.as_view(), name="msg_delete"),
    url(r'^bericht/(?P<pk>\d+)/haltes.geojson', MessageStopsAjaxView.as_view(), name="msg_stops_ajax"), # LEGACY: map
    url(r'^bericht/(?P<pk>\d+)/halte_bereik.geojson', MessageStopsBoundAjaxView.as_view(), name="msg_bounds_ajax"), # Map bounds to zoom

    # This next view is used as URL when adding a message (name is not used)
    url(r'^bericht/haltes.json', ActiveStopsAjaxView.as_view(), name="active_stops_ajax"),

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

    # Kv17 views
    url(r'^ritaanpassing$', ChangeListView.as_view(), name="change_index"),
    url(r'^ritaanpassing/add$', ChangeCreateView.as_view(), name="change_add"),
    # url(r'^ritaanpassing/alles_opheffen$', CancelLinesView.as_view(), name="change_redbutton"),
    url(r'^ritaanpassing/(?P<pk>\d+)/verwijderen$', ChangeDeleteView.as_view(), name="change_delete"),
    url(r'^ritaanpassing/(?P<pk>\d+)/herstellen', ChangeUpdateView.as_view(), name="change_redo"),
    url(r'^ritaanpassing/ritten.json$', ActiveJourneysAjaxView.as_view(), name="active_journeys_ajax"),

    url(r'^vervoerder/wijzig', ChangeCompanyView.as_view(), name="company_change"),
    url(r'^vervoerder/filter/halte/nieuw', FilterStopCreateView.as_view(), name="filter_stop_add"),
    url(r'^vervoerder/filter/halte/(?P<pk>\d+)/verwijderen', FilterStopDeleteView.as_view(), name="filter_stop_delete"),
    url(r'^vervoerder/filter/nieuw', FilterCreateView.as_view(), name="filter_add"),
    url(r'^vervoerder/filter/(?P<pk>\d+)/bewerk', FilterUpdateView.as_view(), name="filter_edit"),
    url(r'^vervoerder/filter/(?P<pk>\d+)/verwijderen$', FilterDeleteView.as_view(), name="filter_delete"),
    url(r'^vervoerder/filter', FilterListView.as_view(), name="filter_list"),
]
