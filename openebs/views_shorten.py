import logging
from braces.views import LoginRequiredMixin
from datetime import date, timedelta, datetime
from django.urls import reverse_lazy
#from django.db.models import Q, F, Count
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, DeleteView#,  TemplateView, ListView
from kv1.models import Kv1Journey, Kv1Stop#, Kv1Line
from openebs.form_kv17 import Kv17ShortenForm#, Kv17ChangeForm
from openebs.models import Kv17Shorten, Kv17Change#, Kv1StopFilter
from openebs.views_push import Kv17PushMixin
from openebs.views_utils import FilterDataownerMixin
from utils.time import get_operator_date, get_operator_date_aware, seconds_to_hhmm
from utils.views import AccessMixin, JSONListResponseMixin#, ExternalMessagePushMixin
from django.utils.dateparse import parse_date
#from django.utils.timezone import now
from djgeojson.views import GeoJSONLayerView
from django.contrib.gis.db.models import Extent

log = logging.getLogger('openebs.views.changes')


class ShortenCreateView(AccessMixin, Kv17PushMixin, CreateView):
    permission_required = 'openebs.add_change'
    model = Kv17Shorten
    form_class = Kv17ShortenForm
    success_url = reverse_lazy('change_index')

    def get_form_kwargs(self):
        kwargs = super(ShortenCreateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(ShortenCreateView, self).get_context_data(**kwargs)
        data['operator_date'] = get_operator_date()
        if 'journey' in self.request.GET:
            self.add_journeys_from_request(data)
            self.add_stops_from_request(data)
        return data

    def add_journeys_from_request(self, data):
        journey_errors = 0
        journeys = []

        for journeynumber in self.request.GET['journey'].split(','):
            if journeynumber == "":
                continue
            log.info("Finding journey %s for '%s'" % (journeynumber, self.request.user))
            j = Kv1Journey.find_from_realtime(self.request.user.userprofile.company, journeynumber)
            if j:
                journeynumber.append(j)
            else:
                journey_errors += 1
                log.error("User '%s' (%s) failed to find journey '%s' " % (
                    self.request.user, self.request.user.userprofile.company, journeynumber))
        data['journeys'] = journeys
        if journey_errors > 0:
            data['journey_errors'] = journey_errors

    def form_invalid(self, form):
        log.error("Form for KV17 shorten invalid!")
        print(form.errors)
        return super(ShortenCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.dataownercode = self.request.user.userprofile.company

        # TODO this is a bad solution - totally gets rid of any benefit of Django's CBV and Forms
        xml = form.save()

        if len(xml) == 0:
            log.error("Tried to communicate KV17 empty line change, rejecting")
            # This is kinda weird, but shouldn't happen, everything has validation
            return HttpResponseRedirect(self.success_url)

        # Push message to GOVI
        if self.push_message(xml):
            log.info("Sent KV17 line change to subscribers: %s" % self.request.POST.get('journeys', "<unknown>"))
        else:
            log.error("Failed to communicate KV17 line change to subscribers")

        # Another hack to redirect correctly
        return HttpResponseRedirect(self.success_url)


class ShortenDetailsView(AccessMixin, FilterDataownerMixin, DetailView):
    permission_required = 'openebs.view_shorten'
    permission_level = 'read'
    model = Kv17Change
    template_name = 'openebs/kv17shorten_detail.html'


class ShortenStopsBoundAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Stop
    render_object = 'object'

    def get_object(self, **kwargs):
        qry = self.get_queryset()
        return {'extent': qry.aggregate(Extent('location')).get('location__extent')}

    def get_queryset(self):
        qry = super(ShortenStopsBoundAjaxView, self).get_queryset()
        pk = self.request.GET.get('id', None)
        qry = qry.filter(stop_shorten__change_id=pk)

        if not (self.request.user.has_perm("openebs.view_all")):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)

        return qry


class ActiveStopsAjaxView_shorten(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv17Shorten
    render_object = 'object'

    def get_object(self):
        operating_day = parse_date(self.request.GET['operatingday']) if 'operatingday' in \
                                                                        self.request.GET else get_operator_date()

        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(change__operatingday=operating_day,
                                             change__is_recovered=False,
                                             change__dataownercode=self.request.user.userprofile.company).distinct()
        return list(queryset.values('change__line', 'change__journey', 'change__dataownercode', 'stop__userstopcode',
                                    'change__is_recovered'))


class ActiveShortenForStopView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    """
    Show shorten journeys on an active stop on the map, creates JSON
    """
    model = Kv1Stop
    render_object = 'object'

    def get_queryset(self):
        tpc = self.kwargs.get('tpc', None)
        if tpc is None or tpc == '0':
            return None
        operatingday = get_operator_date_aware()

        # active list updates at 4 am.
        if datetime.now().hour < 4:
            change = -1
        else:
            change = 0

        change_day = operatingday + timedelta(days=change)

        qry = self.model.objects.filter(stop_shorten__change__operatingday__gte=change_day,
                                        stop_shorten__change__is_recovered=False,
                                        timingpointcode=tpc)
        if not self.request.user.has_perm("openebs.view_all"):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)

        return list({'id': x['id'], 'dataownercode': x['dataownercode'],
                     'operatingday': x['stop_shorten__change__operatingday'].strftime('%d-%m-%Y'),
                     'journeynumber': x['stop_shorten__change__journey__journeynumber'],
                     'departuretime': seconds_to_hhmm(x['stop_shorten__change__journey__departuretime'])}
                    for x in qry.values('id', 'dataownercode', 'stop_shorten__change_id',
                                        'stop_shorten__change__operatingday',
                                        'stop_shorten__change__journey__journeynumber',
                                        'stop_shorten__change__journey__departuretime')
                    .order_by('stop_shorten__change__operatingday', 'stop_shorten__change__journey__departuretime'))

    def get_object(self):
        return list(self.get_queryset())


class ActiveShortenStopListView(LoginRequiredMixin, GeoJSONLayerView):
    """
    Show stops with active messages on the map, creates GeoJSON
    """
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['id', 'name', 'userstopcode', 'dataownercode', 'timingpointcode']

    def get_queryset(self):
        today = date.today()
        qry = self.model.objects.filter(stop_shorten__change__operatingday__gte=today,
                                        stop_shorten__change__is_recovered=False)

        if not self.request.user.has_perm("openebs.view_all"):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        return qry