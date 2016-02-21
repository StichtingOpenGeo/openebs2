import logging

from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.edit import CreateView

from ferry.models import FerryKv6Messages
from kv1.models import Kv1Line
from openebs.views_generic import TemplateRequestView
from openebs.views_push import Kv6PushMixin, Kv17PushMixin
from utils.views import AccessMixin

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