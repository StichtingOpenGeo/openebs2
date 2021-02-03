import logging
from datetime import timedelta, datetime, time
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from kv1.models import Kv1Journey, Kv1Line
from openebs.form_kv17 import Kv17ChangeForm
from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from openebs.views_utils import FilterDataownerMixin
from utils.time import get_operator_date, get_operator_date_aware
from utils.views import AccessMixin, JSONListResponseMixin, AccessJsonMixin
from django.utils.dateparse import parse_date
from django.utils.timezone import now, make_aware


log = logging.getLogger('openebs.views.changes')


class ChangeListView(AccessMixin, ListView):
    permission_required = 'openebs.view_change'
    model = Kv17Change

    def get_context_data(self, **kwargs):
        context = super(ChangeListView, self).get_context_data(**kwargs)
        operatingday = get_operator_date_aware()

        # active list updates at 4 am.
        if datetime.now().hour < 4:
            change = -1
        else:
            change = 0

        change_day = operatingday + timedelta(days=change)

        # Get the currently active changes
        context['active_list'] = self.model.objects.filter(Q(endtime__gte=now()) | Q(endtime__isnull=True) &
                                                           Q(operatingday__gte=change_day),
                                                           is_recovered=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('line__publiclinenumber', 'line__headsign',
                                                                 'operatingday', 'journey__departuretime')

        # Add the no longer active changes
        context['archive_list'] = self.model.objects.filter(Q(endtime__lt=now()) | Q(is_recovered=True) |
                                                            (Q(endtime__isnull=True) & Q(operatingday__lt=change_day)),
                                                            dataownercode=self.request.user.userprofile.company,
                                                            created__gt=operatingday-timedelta(days=3))
        context['archive_list'] = context['archive_list'].order_by('-operatingday', 'line__publiclinenumber',
                                                                   '-journey__departuretime')
        return context


class ChangeCreateView(AccessMixin, Kv17PushMixin, CreateView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    form_class = Kv17ChangeForm
    success_url = reverse_lazy('change_index')

    def get_form_kwargs(self):
        kwargs = super(ChangeCreateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(ChangeCreateView, self).get_context_data(**kwargs)
        data['operator_date'] = get_operator_date()
        if 'journey' in self.request.GET:
            self.add_journeys_from_request(data)
        return data

    def add_journeys_from_request(self, data):
        operating_day = parse_date(
            self.request.GET['operatingday']) if 'operatingday' in self.request.GET else get_operator_date()
        data['operator_date'] = operating_day

        journey_errors = 0
        journeys = []
        for journey in self.request.GET['journey'].split(','):
            if len(journey.strip()) == 0:
                continue
            log.info("Finding journey %s for '%s'" % (journey, self.request.user))
            j = Kv1Journey.find_from_realtime(self.request.user.userprofile.company, journey)
            if j:
                journeys.append(j)
            else:
                journey_errors += 1
                log.error("User '%s' (%s) failed to find journey '%s' " % (self.request.user, self.request.user.userprofile.company, journey))
        data['journeys'] = journeys
        if journey_errors > 0:
            data['journey_errors'] = journey_errors

    def form_invalid(self, form):
        log.error("Form for KV17 change invalid!")
        return super(ChangeCreateView, self).form_invalid(form)

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


class ChangeDeleteView(AccessMixin, Kv17PushMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    success_url = reverse_lazy('change_index')

    def delete(self, request, *args, **kwargs):
        ret = super(ChangeDeleteView, self).delete(request, *args, **kwargs)
        obj = self.get_object()
        if self.push_message(obj.to_xml()):
            log.error("Recovered line succesfully communicated to subscribers: %s" % obj)
        else:
            log.error("Failed to send recover request to subscribers: %s" % obj)
            # We failed to push, recover our delete operation
            obj.is_recovered = False
            obj.recovered = None
            obj.save() # Note, this won't work locally!
        return ret


class ChangeUpdateView(AccessMixin, Kv17PushMixin, FilterDataownerMixin, DeleteView):
    """ This is a really weird view - it's redoing a change that you deleted   """
    permission_required = 'openebs.add_change'
    model = Kv17Change
    success_url = reverse_lazy('change_index')

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
            log.error("Redo line cancel succesfully communicated to subscribers: %s" % obj)
        else:
            log.error("Failed to send redo request to subscribers: %s" % obj)
            # We failed to push, recover our redo operation by restoring previous state
            obj.is_recovered = self.get_object.is_recovered
            obj.recovered = self.get_object.recovered
            obj.save()  # Note, this won't work locally!
        return HttpResponseRedirect(self.get_success_url())

"""
TODO : This is a big red button view allowing you to cancel all active trips if you so wish.
"""
# class CancelLinesView(AccessMixin, Kv17PushMixin, FormView):
#
#     permission_required = 'openebs.add_change'
#     form_class = CancelLinesForm
#     template_name = 'openebs/kv17change_redbutton.html'
#     success_url = reverse_lazy('change_index')
#
#     def get_context_data(self, **kwargs):
#         """ Add data about the trips we'd be cancelling """
#         data = super(CancelLinesView, self).get_context_data(**kwargs)
#         data['trips'] = Kv17Change.objects.filter(dataownercode=self.request.user.userprofile.company)
#         return data
#
#     def form_valid(self, form):
#         ret = super(CancelLinesView, self).form_valid(form)
#         # Find our scenario
#         # Plan messages
#
#         # Concatenate XML for a single request
#         message_string = ""
#         if self.push_message(message_string):
#             log.error("Planned messages sent to subscribers: %s" % "")
#         else:
#             log.error("Failed to communicate planned messages to subscribers: %s")
#         return ret


class ActiveJourneysAjaxView(AccessJsonMixin, JSONListResponseMixin, DetailView):
    permission_required = 'openebs.view_change'
    model = Kv17Change
    render_object = 'object'

    def get_object(self):
        operating_day = parse_date(self.request.GET['operatingday']) if 'operatingday' in \
                                                                        self.request.GET else get_operator_date()
        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(operatingday=operating_day,
                                             is_recovered=False,
                                             dataownercode=self.request.user.userprofile.company).distinct()
        return list(queryset.values('journey_id', 'dataownercode', 'is_recovered'))


class ActiveLinesAjaxView(AccessJsonMixin, JSONListResponseMixin, DetailView):
    permission_required = 'openebs.view_change'
    model = Kv17Change
    render_object = 'object'

    def get_object(self):
        operating_day = parse_date(self.request.GET['operatingday']) if 'operatingday' in self.request.GET else get_operator_date()

        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(Q(is_alljourneysofline=True) | Q(is_alllines=True),
                                             operatingday=operating_day, is_recovered=False,
                                             dataownercode=self.request.user.userprofile.company).distinct()
        # TODO: is it possible to apply a function on a value of a queryset?
        start_of_day = datetime.combine(operating_day, datetime.min.time()).timestamp()
        return list({'id': x['line'],
                     'begintime': int(x['begintime'].timestamp() - start_of_day) if x['begintime'] is not None else None,
                     'endtime': int(x['endtime'].timestamp() - start_of_day) if x['endtime'] is not None else None,
                     'dataownercode': x['dataownercode'], 'alljourneysofline': x['is_alljourneysofline'],
                     'all_lines': x['is_alllines']}
                    for x in queryset.values('line', 'begintime', 'endtime', 'dataownercode', 'is_alljourneysofline',
                    'is_alllines'))


class ChangeValidationAjaxView(AccessJsonMixin, JSONListResponseMixin, DetailView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    render_object = 'object'

    def get_object(self):  # should be redundant after jquery filter in html-form, but just in case
        change_validation = []
        operatingday = parse_date(self.request.GET.get('operatingday'))
        journeys = self.request.GET.get('journeys')
        lines = self.request.GET.get('lines')
        begintime_part = self.request.GET.get('begintime')
        endtime_part = self.request.GET.get('endtime')

        if operatingday is None:
            change_validation.append("Er staan geen ritten in de database")

        if begintime_part != '':
            hh, mm = begintime_part.split(':')
            begintime = make_aware(datetime.combine(operatingday, time(int(hh), int(mm))))
        else:
            begintime = None

        if endtime_part != '':
            hh_e, mm_e = endtime_part.split(':')
            endtime = make_aware(datetime.combine(operatingday, time(int(hh_e), int(mm_e))))
            if begintime:
                if begintime > endtime:  # if endtime before begintime
                    endtime = endtime + timedelta(days=1)  # endtime is next day
                    if endtime.time() >= time(6, 0):  # and after 6 am: validation error
                        change_validation.append("Eindtijd valt op volgende operationele dag")
        else:
            endtime = None

        dataownercode = self.request.user.userprofile.company
        if 'Alle ritten' in journeys:
            change_validation = self.clean_all_journeys(operatingday, dataownercode, lines, begintime, endtime,
                                                        change_validation)
        elif 'Hele vervoerder' in lines:
            change_validation = self.clean_all_lines(operatingday, dataownercode, begintime, endtime, change_validation)
        else:
            change_validation = self.clean_journeys(operatingday, dataownercode, journeys, change_validation)

        return change_validation

    def clean_journeys(self, operatingday, dataownercode, journeys, change_validation):
        valid_journeys = 0
        if journeys != '':
            for journey in journeys.split(',')[0:-1]:
                journey_qry = Kv1Journey.objects.filter(dataownercode=dataownercode, pk=journey, dates__date=operatingday)
                if journey_qry.count() == 0:
                    change_validation.append("Een of meer geselecteerde ritten zijn ongeldig")
                else:
                    valid_journeys += 1

                # delete recovered if query is the same.
                Kv17Change.objects.filter(dataownercode=dataownercode, journey__pk=journey, line=journey_qry[0].line,
                                          operatingday=operatingday, is_recovered=True).delete()
        if valid_journeys == 0:
            change_validation.append("Er zijn geen ritten geselecteerd om op te heffen")

        return change_validation

    def clean_all_journeys(self, operatingday, dataownercode, lines, begintime, endtime, change_validation):
        if lines != '':
            for line in lines.split(',')[0:-1]:
                line_qry = Kv1Line.objects.filter(pk=line)

                if line_qry.count() == 0:
                    change_validation.append("Geen lijn gevonden.")
                    continue

                database_alljourneys = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                                 is_alljourneysofline=True, line=line_qry[0],
                                                                 operatingday=operatingday, is_recovered=False)

                database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode,
                                                              is_alllines=True, operatingday=operatingday,
                                                              is_recovered=False)

                # delete recovered if query is the same.
                Kv17Change.objects.filter(dataownercode=dataownercode, is_alljourneysofline=True, line=line_qry[0],
                                          operatingday=operatingday, begintime=begintime, endtime=endtime,
                                          is_recovered=True).delete()

                if operatingday == datetime.today().date():
                    begintime = make_aware(datetime.now()) if begintime is None else begintime
                else:
                    begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                        if begintime is None else begintime

                if database_alllines:
                    if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                Q(begintime__lte=begintime) | Q(begintime=None)):
                        change_validation.append(
                            "De gehele vervoerder is al aangepast voor de aangegeven ingangstijd.")

                elif database_alljourneys:
                    if database_alljourneys.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                                   Q(begintime__lte=begintime) | Q(begintime=None)):
                        change_validation.append(
                            "Een of meer geselecteerde lijnen zijn al aangepast voor de aangegeven ingangstijd.")

        return change_validation

    def clean_all_lines(self, operatingday, dataownercode, begintime, endtime, change_validation):
        database_alllines = Kv17Change.objects.filter(dataownercode=dataownercode, is_alllines=True,
                                                      operatingday=operatingday, is_recovered=False)

        # delete recovered if query is the same.
        Kv17Change.objects.filter(dataownercode=dataownercode, is_alllines=True, is_recovered=True,
                                  operatingday=operatingday, begintime=begintime, endtime=endtime).delete()

        if database_alllines:
            if operatingday == datetime.today().date():
                begintime = make_aware(datetime.now()) if begintime is None else begintime
            else:
                begintime = make_aware(datetime.combine(operatingday, time((int(4))))) \
                    if begintime is None else begintime

            if database_alllines.filter(Q(endtime__gt=begintime) | Q(endtime=None),
                                        Q(begintime__lte=begintime) | Q(begintime=None)):
                change_validation.append("De ingangstijd valt al binnen een geplande operatie.")

        return change_validation
