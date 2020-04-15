import logging
from braces.views import LoginRequiredMixin
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils.dateparse import parse_date

from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from kv1.models import Kv1Line, Kv1JourneyDate
from openebs.form_line_cancel import ChangeLineCancelCreateForm
from openebs.models import Kv17ChangeLine
from openebs.views_push import Kv17PushMixin
from openebs.views_utils import FilterDataownerMixin
from utils.time import get_operator_date, get_operator_date_aware
from utils.views import AccessMixin, ExternalMessagePushMixin, JSONListResponseMixin

log = logging.getLogger('openebs.views.change_line_cancel')


class ChangeLineCancelListView(AccessMixin, ListView):
    permission_required = 'openebs.view_change_line'
    model = Kv17ChangeLine

    def get_context_data(self, **kwargs):
        context = super(ChangeLineCancelListView, self).get_context_data(**kwargs)

        # active list updates at 4 am.
        if datetime.now().hour < 4:
            change = -1
        else:
            change = 0
        change_day = get_operator_date() + timedelta(days=change)

        # Get the currently active changes
        context['active_list'] = self.model.objects.filter(Q(endtime__gte=now()) | (Q(endtime__isnull=True) & Q(operatingday__gte=change_day)), is_recovered=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('line__publiclinenumber', 'line__lineplanningnumber', 'begintime', 'endtime')

        # Add the no longer active changes
        context['archive_list'] = self.model.objects.filter(Q(endtime__lt=now()) | Q(is_recovered=True) | (Q(endtime__isnull=True) & Q(operatingday__lt=change_day)),
                                                            dataownercode=self.request.user.userprofile.company,
                                                            created__gt=get_operator_date_aware()-timedelta(days=3))
        context['archive_list'] = context['archive_list'].order_by('-operatingday', 'line__publiclinenumber', 'begintime', 'endtime')

        return context


class ChangeLineCancelCreateView(AccessMixin, Kv17PushMixin, CreateView):
    permission_required = 'openebs.add_change_line'
    model = Kv17ChangeLine
    form_class = ChangeLineCancelCreateForm
    template_name = 'openebs/kv17changeline_form.html'
    success_url = reverse_lazy('change_line_index')

    def get_context_data(self, **kwargs):
        data = super(ChangeLineCancelCreateView, self).get_context_data(**kwargs)
        self.get_lines(data)
        self.get_days(data)
        return data

    def get_lines(self, data):
        lines = Kv1Line.objects.all() \
            .filter(dataownercode=self.request.user.userprofile.company) \
            .values('publiclinenumber', 'headsign', 'dataownercode') \
            .order_by('publiclinenumber')
        data['header'] = ['Lijn', 'Eindbestemming']
        data['lines'] = lines

    def get_days(self, data):
        database = Kv1JourneyDate.objects.all() \
            .values('date').distinct('date') \
            .filter(date__gte=datetime.today() - timedelta(days=1))
        data['days_in_database'] = len(database)

    def form_invalid(self, form):
        log.error("Form for KV17 change invalid!")
        return super(ChangeLineCancelCreateView, self).form_invalid(form)

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
            log.info("Sent KV17 line change to subscribers: %s" % self.request.POST.get("lijnen", "<unknown>"))
        else:
            log.error("Failed to communicate KV17 line change to subscribers")

        # Another hack to redirect correctly
        return HttpResponseRedirect(self.success_url)


class ChangeLineCancelDeleteView(AccessMixin, Kv17PushMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_change_line'
    model = Kv17ChangeLine
    success_url = reverse_lazy('change_line_index')

    def delete(self, request, *args, **kwargs):
        ret = super(ChangeLineCancelDeleteView, self).delete(request, *args, **kwargs)
        obj = self.get_object()
        if self.push_message(obj.to_xml()):
            log.error("Recovered line successfully communicated to subscribers: %s" % obj)
        else:
            log.error("Failed to send recover request to subscribers: %s" % obj)
            # We failed to push, recover our delete operation
            obj.is_recovered = False
            obj.recovered = None
            obj.save() # Note, this won't work locally!
        return ret


class ChangeLineCancelUpdateView(AccessMixin, Kv17PushMixin, FilterDataownerMixin, DeleteView):
    """ This is a really weird view - it's redoing a change that you deleted   """
    permission_required = 'openebs.add_change_line'
    model = Kv17ChangeLine
    success_url = reverse_lazy('change_line_index')

    def update_object(self):
        obj = self.get_object()
        obj.is_recovered = False
        obj.recovered = None
        obj.save()
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()  # Store an original to undo our redo
        obj = self.update_object()
        if self.push_message(obj.to_xml()):
            log.info("Redo line cancel successfully communicated to subscribers: %s" % obj)
        else:
            log.error("Failed to send redo request to subscribers: %s" % obj)
            # We failed to push, recover our redo operation by restoring previous state
            obj.is_recovered = self.get_object.is_recovered
            obj.recovered = self.get_object.recovered
            obj.save()  # Note, this won't work locally!
        return HttpResponseRedirect(self.get_success_url())


class ActiveLinesAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv17ChangeLine
    form_class = ChangeLineCancelCreateForm
    render_object = 'object'

    def get_object(self):
        operating_day = get_operator_date()
        if 'operatingday' in self.request.GET:
            operating_day = parse_date(self.request.GET['operatingday'])

        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(operatingday=operating_day,
                                             is_recovered=False,
                                             # These two are double, but just in case
                                             #changes__dataownercode=self.request.user.userprofile.company,
                                             dataownercode=self.request.user.userprofile.company).distinct()

        # TODO: is it possible to apply a function on a value of a queryset?
        start_of_day = datetime.combine(operating_day, datetime.min.time()).timestamp()
        return list({'id': x['line'], 'begintime': int(x['begintime'].timestamp() - start_of_day) if x['begintime'] is not None else None, 'endtime': int(x['endtime'].timestamp() - start_of_day) if x['endtime'] is not None else None, 'dataownercode': x['dataownercode']} for x in queryset.values('begintime', 'endtime', 'line', 'dataownercode'))