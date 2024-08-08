from django.urls import re_path
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
from openebs.views_shorten import ShortenCreateView, ShortenDetailsView, ShortenedJourneysAjaxView

urlpatterns = [
    # Onze Index
    re_path(r'^$', RedirectView.as_view(url='/bericht', permanent=True), name='index'),

    # Kaart views
    re_path(r'^kaart$', TemplateRequestView.as_view(template_name='openebs/kv15stopmessage_map.html'), name="msg_map"),

    # Berichten views
    re_path(r'^bericht$', MessageListView.as_view(), name="msg_index"),
    re_path(r'^bericht/nieuw$', MessageCreateView.as_view(), name="msg_add"),
    re_path(r'^bericht/(?P<pk>\d+)/bekijken', MessageDetailsView.as_view(), name="msg_view"),
    re_path(r'^bericht/(?P<pk>\d+)/bewerken$', MessageUpdateView.as_view(), name="msg_edit"),
    re_path(r'^bericht/(?P<pk>\d+)/herhaal', MessageResendView.as_view(), name="msg_resend"),
    re_path(r'^bericht/(?P<pk>\d+)/verwijderen$', MessageDeleteView.as_view(), name="msg_delete"),
    re_path(r'^bericht/(?P<pk>\d+)/haltes.geojson', MessageStopsAjaxView.as_view(), name="msg_stops_ajax"), # LEGACY: map
    re_path(r'^bericht/(?P<pk>\d+)/halte_bereik.geojson', MessageStopsBoundAjaxView.as_view(), name="msg_bounds_ajax"), # Map bounds to zoom
    re_path(r'^bericht/importeren', MessageImportView.as_view(), name="msg_import"),
    re_path(r'^bericht/(?P<pk>\d+)/haltes$', ActiveMessageAjaxView.as_view(), name="msg_active"),

    # This next view is used as URL when adding a message (name is not used)
    re_path(r'^bericht/haltes.json', ActiveStopsAjaxView.as_view(), name="active_stops_ajax"),

    # Scenario views
    re_path(r'^scenario$', ScenarioListView.as_view(), name="scenario_index"),
    re_path(r'^scenario/nieuw$', ScenarioCreateView.as_view(), name="scenario_add"),
    re_path(r'^scenario/(?P<pk>\d+)/bewerk', ScenarioUpdateView.as_view(), name="scenario_edit"),
    re_path(r'^scenario/(?P<pk>\d+)/dupliceer', ScenarioCloneView.as_view(), name="scenario_clone"),
    re_path(r'^scenario/(?P<pk>\d+)/verwijderen', ScenarioDeleteView.as_view(), name="scenario_delete"),
    re_path(r'^scenario/(?P<scenario>\d+)/inplannen', PlanScenarioView.as_view(), name="scenario_plan"),
    re_path(r'^scenario/(?P<scenario>\d+)/bericht/nieuw$', ScenarioMessageCreateView.as_view(), name="scenario_msg_add"),
    re_path(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/bewerken', ScenarioMessageUpdateView.as_view(), name="scenario_msg_edit"),
    re_path(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/verwijderen', ScenarioMessageDeleteView.as_view(), name="scenario_msg_delete"),
    re_path(r'^scenario/(?P<scenario>\d+)/haltes.geojson', ScenarioStopsAjaxView.as_view(), name="scenario_stops_ajax"),
    re_path(r'^scenario/(?P<scenario>\d+)/durationtypes.json', ScenarioMessageAjaxView.as_view(), name="scenario_durations_ajax"),
    re_path(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/bekijken', ScenarioMessageDetailsView.as_view(), name="scenario_msg_view"),
    re_path(r'^scenario/(?P<scenario>\d+)/halte_bereik.geojson', ScenarioStopsBoundAjaxView.as_view(), name="scenario_bounds_ajax"),  # Map bounds to zoom
    re_path(r'^scenario/(?P<scenario>\d+)/kaart', TemplateRequestView.as_view(template_name='openebs/kv15scenario_map.html'), name='scenario_msg_map'),
    re_path(r'^scenario/(?P<scenario>\d+)/(?P<tpc>\w+)/messages.json$', ScenarioMessagesForStopView.as_view(), name="scenariomsg_stop_json"),
    re_path(r'^scenario/(?P<scenario>\d+)/messages.json$', ScenarioActiveMessagesAjaxView.as_view(), name="scenario_message_ids"),
    re_path(r'^scenario/(?P<scenario>\d+)/bericht/(?P<pk>\d+)/haltes', ScenarioMessageAjaxView.as_view(), name="scenario_msg_stops"),

    # Kv17 views
    re_path(r'^ritaanpassing$', ChangeListView.as_view(), name="change_index"),
    re_path(r'^ritaanpassing/add$', ChangeCreateView.as_view(), name="change_add"),
    # url(r'^ritaanpassing/alles_opheffen$', CancelLinesView.as_view(), name="change_redbutton"),
    re_path(r'^ritaanpassing/(?P<pk>\d+)/verwijderen$', ChangeDeleteView.as_view(), name="change_delete"),
    re_path(r'^ritaanpassing/(?P<pk>\d+)/herstellen', ChangeUpdateView.as_view(), name="change_redo"),
    re_path(r'^ritaanpassing/ritten.json$', ActiveJourneysAjaxView.as_view(), name="active_journeys_ajax"),
    re_path(r'^ritaanpassing/lijnen.json$', ActiveLinesAjaxView.as_view(), name="active_lines_ajax"),
    re_path(r'^ritaanpassing/ritten-nietgevolgd.json$', NotMonitoredJourneyAjaxView.as_view(), name="notMonitored_journeys_ajax"),
    re_path(r'^ritaanpassing/lijnen-nietgevolgd.json$', NotMonitoredLinesAjaxView.as_view(), name="notMonitored_lines_ajax"),

    re_path(r'^ritinkorting/add', ShortenCreateView.as_view(), name="shorten_add"),
    re_path(r'^ritinkorting/(?P<pk>\d+)/bekijken', ShortenDetailsView.as_view(), name="shorten_view"),
    re_path(r'^ritinkorting/ritten.json$', ShortenedJourneysAjaxView.as_view(), name="shortened_journeys_ajax"),

    re_path(r'^vervoerder/wijzig', ChangeCompanyView.as_view(), name="company_change"),
    re_path(r'^vervoerder/filter/halte/nieuw', FilterStopCreateView.as_view(), name="filter_stop_add"),
    re_path(r'^vervoerder/filter/halte/(?P<pk>\d+)/verwijderen', FilterStopDeleteView.as_view(), name="filter_stop_delete"),
    re_path(r'^vervoerder/filter/nieuw', FilterCreateView.as_view(), name="filter_add"),
    re_path(r'^vervoerder/filter/(?P<pk>\d+)/bewerk', FilterUpdateView.as_view(), name="filter_edit"),
    re_path(r'^vervoerder/filter/(?P<pk>\d+)/verwijderen$', FilterDeleteView.as_view(), name="filter_delete"),
    re_path(r'^vervoerder/filter', FilterListView.as_view(), name="filter_list"),
]
