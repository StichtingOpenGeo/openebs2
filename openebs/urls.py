from django.conf.urls import url
from django.views.generic import RedirectView
from openebs.views import MessageListView, MessageCreateView, MessageDeleteView, MessageUpdateView, ActiveStopsAjaxView, MessageDetailsView, MessageStopsAjaxView, \
    MessageStopsBoundAjaxView, MessageResendView, MessageImportView, ActiveMessageAjaxView
from openebs.views_change import ChangeListView, ChangeCreateView, ChangeDeleteView, ActiveJourneysAjaxView, \
    ChangeUpdateView, ActiveLinesAjaxView, NotMonitoredJourneyAjaxView, NotMonitoredLinesAjaxView
from openebs.views_filters import FilterListView, FilterDeleteView, FilterUpdateView, FilterCreateView, \
    FilterStopCreateView, FilterStopDeleteView
from openebs.views_generic import ChangeCompanyView, TemplateRequestView
from openebs.views_scenario import ScenarioListView, ScenarioCreateView, ScenarioUpdateView, ScenarioDeleteView, \
    PlanScenarioView, ScenarioStopsAjaxView, ScenarioMessageAjaxView, ScenarioCloneView, ScenarioStopsBoundAjaxView, \
    ScenarioMessagesForStopView, ScenarioActiveMessagesAjaxView
from openebs.views_scenario_msg import ScenarioMessageCreateView, ScenarioMessageUpdateView, ScenarioMessageDeleteView, \
    ScenarioMessageDetailsView, ScenarioMessageAjaxView
from openebs.views_shorten import ShortenCreateView, ShortenDetailsView, ShortenStopsBoundAjaxView, \
    ActiveStopsAjaxViewShorten, ActiveShortenForStopView, ActiveShortenStopListView

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
    url(r'^bericht/importeren', MessageImportView.as_view(), name="msg_import"),
    url(r'^bericht/(?P<pk>\d+)/haltes$', ActiveMessageAjaxView.as_view(), name="msg_active"),

    # This next view is used as URL when adding a message (name is not used)
    url(r'^bericht/haltes.json', ActiveStopsAjaxView.as_view(), name="active_stops_ajax"),

    # Scenario views
    url(r'^scenario$', ScenarioListView.as_view(), name="scenario_index"),
    url(r'^scenario/nieuw$', ScenarioCreateView.as_view(), name="scenario_add"),
    url(r'^scenario/(?P<pk>\d+)/bewerk', ScenarioUpdateView.as_view(), name="scenario_edit"),
    url(r'^scenario/(?P<pk>\d+)/dupliceer', ScenarioCloneView.as_view(), name="scenario_clone"),
    url(r'^scenario/(?P<pk>\d+)/verwijderen', ScenarioDeleteView.as_view(), name="scenario_delete"),
    url(r'^scenario/(?P<scenario>\d+)/inplannen', PlanScenarioView.as_view(), name="scenario_plan"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/nieuw$', ScenarioMessageCreateView.as_view(), name="scenario_msg_add"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/bewerken', ScenarioMessageUpdateView.as_view(), name="scenario_msg_edit"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/verwijderen', ScenarioMessageDeleteView.as_view(), name="scenario_msg_delete"),
    url(r'^scenario/(?P<scenario>\d+)/haltes.geojson', ScenarioStopsAjaxView.as_view(), name="scenario_stops_ajax"),
    url(r'^scenario/(?P<scenario>\d+)/durationtypes.json', ScenarioMessageAjaxView.as_view(), name="scenario_durations_ajax"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/bekijken', ScenarioMessageDetailsView.as_view(), name="scenario_msg_view"),
    url(r'^scenario/(?P<scenario>\d+)/halte_bereik.geojson', ScenarioStopsBoundAjaxView.as_view(), name="scenario_bounds_ajax"),  # Map bounds to zoom
    url(r'^scenario/(?P<scenario>\d+)/kaart', TemplateRequestView.as_view(template_name='openebs/kv15scenario_map.html'), name='scenario_msg_map'),
    url(r'^scenario/(?P<scenario>\d+)/(?P<tpc>\w+)/messages.json$', ScenarioMessagesForStopView.as_view(), name="scenariomsg_stop_json"),
    url(r'^scenario/(?P<scenario>\d+)/messages.json$', ScenarioActiveMessagesAjaxView.as_view(), name="scenario_message_ids"),
    url(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/haltes', ScenarioMessageAjaxView.as_view(), name="scenario_msg_stops"),

    # Kv17 views
    url(r'^ritaanpassing$', ChangeListView.as_view(), name="change_index"),
    url(r'^ritaanpassing/add$', ChangeCreateView.as_view(), name="change_add"),
    # url(r'^ritaanpassing/alles_opheffen$', CancelLinesView.as_view(), name="change_redbutton"),
    url(r'^ritaanpassing/(?P<pk>\d+)/verwijderen$', ChangeDeleteView.as_view(), name="change_delete"),
    url(r'^ritaanpassing/(?P<pk>\d+)/herstellen', ChangeUpdateView.as_view(), name="change_redo"),
    url(r'^ritaanpassing/ritten.json$', ActiveJourneysAjaxView.as_view(), name="active_journeys_ajax"),
    url(r'^ritaanpassing/lijnen.json$', ActiveLinesAjaxView.as_view(), name="active_lines_ajax"),
    url(r'^ritaanpassing/ritten-nietgevolgd.json$', NotMonitoredJourneyAjaxView.as_view(), name="notMonitored_journeys_ajax"),
    url(r'^ritaanpassing/lijnen-nietgevolgd.json$', NotMonitoredLinesAjaxView.as_view(), name="notMonitored_lines_ajax"),

    url(r'^ritinkorting/add', ShortenCreateView.as_view(), name="shorten_add"),
    url(r'^ritinkorting/(?P<pk>\d+)/bekijken', ShortenDetailsView.as_view(), name="shorten_view"),
    url(r'^ritinkorting/kaart', TemplateRequestView.as_view(template_name='openebs/kv17shorten_map.html'), name="shorten_map"),
    url(r'^ritinkorting/halte/(?P<tpc>\w+)/ritten.json$', ActiveShortenForStopView.as_view(), name="shorten_stop_json"),
    url(r'^ritinkorting/active-haltes.geojson$', ActiveShortenStopListView.as_view(), name="shorten_geojson"),
    url(r'^ritinkorting/halte_bereik.geojson$', ShortenStopsBoundAjaxView.as_view(), name="shorten_bounds_ajax"),
    url(r'^ritinkorting/haltes', ActiveStopsAjaxViewShorten.as_view(), name="active_stops_ajax"),

    url(r'^vervoerder/wijzig', ChangeCompanyView.as_view(), name="company_change"),
    url(r'^vervoerder/filter/halte/nieuw', FilterStopCreateView.as_view(), name="filter_stop_add"),
    url(r'^vervoerder/filter/halte/(?P<pk>\d+)/verwijderen', FilterStopDeleteView.as_view(), name="filter_stop_delete"),
    url(r'^vervoerder/filter/nieuw', FilterCreateView.as_view(), name="filter_add"),
    url(r'^vervoerder/filter/(?P<pk>\d+)/bewerk', FilterUpdateView.as_view(), name="filter_edit"),
    url(r'^vervoerder/filter/(?P<pk>\d+)/verwijderen$', FilterDeleteView.as_view(), name="filter_delete"),
    url(r'^vervoerder/filter', FilterListView.as_view(), name="filter_list"),
]
