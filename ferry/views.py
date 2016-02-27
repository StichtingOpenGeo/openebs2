import logging

from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView, ListView
from django.views.generic.edit import CreateView

from ferry.models import FerryKv6Messages
from kv1.models import Kv1Line
from openebs.views_generic import TemplateRequestView
from openebs.views_push import Kv6PushMixin, Kv17PushMixin
from utils.time import get_operator_date
from utils.views import AccessMixin, JSONListResponseMixin

log = logging.getLogger('openebs.ferry.views')


class FerryHomeView(AccessMixin, TemplateRequestView):
    template_name = "ferry/ferry_home.html"
    permission_required = 'openebs.add_messages'

    def get_context_data(self, **kwargs):
        ctx = super(FerryHomeView, self).get_context_data(**kwargs)
        ctx['lines'] = Kv1Line.objects.filter(is_ferry=True, dataownercode=self.request.user.userprofile.company)
        return ctx


class FerryDepartedView(AccessMixin, Kv6PushMixin, CreateView):
    permission_required = 'openebs.add_messages'
    model = FerryKv6Messages
    success_url = reverse_lazy('ferry_home')
    fields = ['line', 'journeynumber', 'departed']

    def form_valid(self, form):
        resp = super(FerryDepartedView, self).form_valid(form)
        xml = self.object.to_kv6_delay()
        if self.push_message(xml):
            log.info("Sent KV6 ferry departed message to subscribers: %s" % self.object.journeynumber)
        else:
            log.error("Failed to communicate Kv6 departed to subscribers: %s" % xml)
        return resp


class FerryCancelledView(AccessMixin, Kv17PushMixin, CreateView):
    permission_required = 'openebs.add_change'
    model = FerryKv6Messages
    success_url = reverse_lazy('ferry_home')
    fields = ['line', 'journeynumber']

    def form_valid(self, form):
        resp = super(FerryCancelledView, self).form_valid(form)
        xml = self.object.to_kv17change()
        if xml and self.push_message(xml):
            log.info("Sent KV17 ferry journey cancelled message to subscribers: %s" % self.object.journeynumber)
        else:
            log.error("Failed to communicate KV17 ferry journey cancelled to subscribers: %s" % xml)
        return resp


class FerrySuspendedView(AccessMixin, Kv17PushMixin, RedirectView):
    permanent = False
    permission_required = 'openebs.add_change'
    url = reverse_lazy('ferry_home')

    def get(self, request, *args, **kwargs):
        resp = super(FerrySuspendedView, self).get(request, *args, **kwargs)
        xml = FerryKv6Messages.cancel_all(self.request.POST.get('line', None))
        if len(xml) > 0 and self.push_message(''.join(xml)):
            log.info("Sent KV17 ferry journey cancelled message to subscribers: %s" % self.object.journeynumber)
        else:
            log.error("Failed to communicate KV17 ferry journey cancelled to subscribers: %s" % xml)

        return resp


class FerryRecoveredView(AccessMixin, Kv17PushMixin, RedirectView):
    permanent = False
    permission_required = 'openebs.add_change'
    url = reverse_lazy('ferry_home')

    def post(self, request, *args, **kwargs):
        resp = super(FerryRecoveredView, self).get(request, *args, **kwargs)
        messages = FerryKv6Messages.objects.filter(line=self.request.POST.get('line', None),
                                                   operatingday=get_operator_date(),
                                                   journeynumber=self.request.POST.get('journeynumber', None))
        xml = []
        for message in messages:
            output = message.to_kv17recover()
            if output:
                xml.append(output)
            else:
                log.info("Couldn't delete message %s" % self.message)
        if len(xml) > 0 and self.push_message(''.join(xml)):
            log.info("Sent KV17 ferry journey cancelled message to subscribers: %s" % self.object.journeynumber)
        else:
            log.error("Failed to communicate KV17 ferry journey cancelled to subscribers: %s" % xml)

        return resp


class FerryTripJsonView(AccessMixin, JSONListResponseMixin, ListView):
    permission_required = 'ferry.add_ferrykv6messages'
    model = Kv1Line
    render_object = 'object'

    def get_context_data(self, **kwargs):
        ctx = super(FerryTripJsonView, self).get_context_data(**kwargs)
        ctx[self.render_object] = self.get_object()
        return ctx

    def get_object(self):
        """
        Forces our output as json and do some queries
        """
        obj = self.get_queryset().get(pk=self.kwargs.get('pk', None))
        if obj:
            ferry = FerryKv6Messages.objects.filter(line=obj, operatingday=get_operator_date())
            ferrytrips = {t.journeynumber: t for t in ferry}
            # Note, the list() is required to serialize correctly
            # We're filtering on todays trips #
            journeys = obj.journeys.filter(dates__date=get_operator_date()).order_by('departuretime') \
                .values('id', 'journeynumber', 'direction', 'departuretime', 'changes__created',
                        'changes__is_recovered')
            return {'outward': self.merge_filter_direction(journeys, 1, ferrytrips),
                    'return': self.merge_filter_direction(journeys, 2, ferrytrips)}

    @staticmethod
    def merge_filter_direction(journeys, direction, ferrytrips):
        lst = list(journeys.filter(direction=direction))
        for journey in lst:
            if journey['journeynumber'] in ferrytrips:
                journey['departed'] = ferrytrips[journey['journeynumber']].departed
                journey['cancelled'] = ferrytrips[journey['journeynumber']].cancelled
                journey['delay'] = ferrytrips[journey['journeynumber']].delay
        return lst
