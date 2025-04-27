import logging

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, DetailView

from kv1.models import Kv1Journey
from openebs.form_kv17 import Kv17ShortenForm
from openebs.models import Kv17Shorten, Kv17Change
from openebs.views_push import Kv17PushMixin
from openebs.views_utils import FilterDataownerMixin
from utils.time import get_operator_date
from utils.views import AccessMixin, JSONListResponseMixin, AccessJsonMixin

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
        return super(ShortenCreateView, self).form_invalid(form)

    def form_valid(self, form):

        """ created SHORTEN already exists """
        if not form.cleaned_data['journeys']:
            return HttpResponseRedirect(self.success_url)

        form.instance.dataownercode = self.request.user.userprofile.company
        form.instance.operatingday = self.request.POST['operatingday']
        form.instance.showcancelledtrip = True if self.request.POST.get('showcancelledtrip', '') == 'on' else False
        form.instance.is_cancel = False  # is SHORTEN
        form.instance.recovered_changes = form.cleaned_data['recovered_changes'] if 'recovered_changes' in \
                                                                                      form.cleaned_data.keys() else []

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



class ShortenedJourneysAjaxView(AccessJsonMixin, JSONListResponseMixin, DetailView):
    permission_required = 'openebs.view_change'
    model = Kv17Change
    render_object = 'object'

    def get_object(self):
        operating_day = parse_date(self.request.GET['operatingday']) if 'operatingday' in \
                                                                        self.request.GET else get_operator_date()
        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(operatingday=operating_day, is_recovered=False,
                                             shorten_details__isnull=False,
                                             dataownercode=self.request.user.userprofile.company).distinct()
        return list(queryset.values('journey_id', 'dataownercode', 'is_recovered', 'shorten_details'))
