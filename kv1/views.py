import json

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from datetime import timedelta, datetime
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from djgeojson.views import GeoJSONLayerView
from utils.calender import CountCalendar
from utils.time import get_operator_date
from utils.views import JSONListResponseMixin
from kv1.models import Kv1Line, Kv1Stop, Kv1JourneyDate
from dateutil.relativedelta import relativedelta

# Views for adding messages and related lookups
class LineSearchView(LoginRequiredMixin, JSONListResponseMixin, ListView):
    model = Kv1Line
    render_object = 'object_list'

    def get_queryset(self):
        qry = super(LineSearchView, self).get_queryset()
        qry = qry.filter(dataownercode=self.request.user.userprofile.company) \
            .order_by('lineplanningnumber') \
            .values('pk', 'dataownercode', 'headsign', 'lineplanningnumber', 'publiclinenumber')
        needle = self.kwargs.get('search', '') or ''
        qry = qry.filter(Q(headsign__icontains=needle) | Q(publiclinenumber__startswith=needle))
        return qry


class LineStopView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Line
    render_object = 'object'

    def get_object(self, queryset=None):
        """
        This is a bit of a hack, but forces our JSON we get out of the db out as JSON again
        """
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk', None))
        if obj:
            return {'stop_map': obj.stop_map if isinstance(obj.stop_map, list) else json.loads(obj.stop_map)}
        return obj # TODO?


class LineTripView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Line
    render_object = 'object'

    def get_object(self, queryset=None):
        """
        Forces our output as json and do some queries
        """
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk', None))
        if obj:
            # Note, the list() is required to serialize correctly
            # We're filtering on todays trips #
            journeys = obj.journeys.filter(dates__date=get_operator_date()).order_by('departuretime') \
                .values('id', 'journeynumber', 'direction', 'departuretime')
            return {'trips_1': list(journeys.filter(direction=1)), 'trips_2': list(journeys.filter(direction=2))}
        return obj


# Map views
class ActiveStopListView(LoginRequiredMixin, GeoJSONLayerView):
    """
    Show stops with active messages on the map, creates GeoJSON
    """
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['id', 'name', 'userstopcode', 'dataownercode', 'timingpointcode']

    def get_queryset(self):
        qry = self.model.objects.filter(messages__stopmessage__messagestarttime__lte=now(),
                                        messages__stopmessage__messageendtime__gte=now(),
                                        messages__stopmessage__isdeleted=False)\
                                .exclude(timingpointcode=0)\
                                .distinct('timingpointcode')
        if not self.request.user.has_perm("openebs.view_all"):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        return qry


class ActiveMessagesForStopView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    """
    Show active messages on an active stop on the map, creates JSON
    """
    model = Kv1Stop
    render_object = 'object'

    def get_queryset(self):
        tpc = self.kwargs.get('tpc', None)
        if tpc is None or tpc == '0':
            return None
        qry = self.model.objects.filter(messages__stopmessage__messagestarttime__lte=now(),
                                        messages__stopmessage__messageendtime__gte=now(),
                                        messages__stopmessage__isdeleted=False,
                                        timingpointcode=tpc).distinct('kv15stopmessage__id')
        if not self.request.user.has_perm("openebs.view_all"):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        return qry.values('id', 'dataownercode', 'kv15stopmessage__dataownercode', 'kv15stopmessage__messagecodenumber',
                          'kv15stopmessage__messagecontent', 'kv15stopmessage__id')

    def get_object(self):
        return list(self.get_queryset())


class StopAutocompleteView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    """
    Search for stops, creates JSON. Used by autocomplete on map and filter creation
    """
    model = Kv1Stop
    render_object = 'object'

    def get_queryset(self):
        term = self.request.GET.get('q', "").lower()
        qry = super(StopAutocompleteView, self).get_queryset()
        if not self.request.user.has_perm("openebs.view_all"):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        result = qry.filter(Q(name__icontains=term) | Q(timingpointcode__startswith=term)).values('id', 'dataownercode',
                                                                                                  'timingpointcode',
                                                                                                  'userstopcode',
                                                                                                  'name', 'location')
        return result

    def get_object(self):
        return list([StopAutocompleteView.fix_loc(stop) for stop in self.get_queryset()])

    @staticmethod
    def fix_loc(stop):
        stop['location'] = [stop['location'].y, stop['location'].x]
        return stop

# Data import details
class DataImportView(LoginRequiredMixin, StaffuserRequiredMixin, ListView):
    """
    Show details about what trips currently in the database
    """
    model = Kv1JourneyDate
    template_name = 'kv1/importdata_list.html'

    def get_context_data(self, **kwargs):
        context = super(DataImportView, self).get_context_data(**kwargs)
        cal = CountCalendar(context['object_list'])
        date_now = datetime.now()
        date_next = date_now + relativedelta(months=1)
        context['calendar'] = mark_safe(
            cal.formatmonth(date_now.year, date_now.month, ) + '<br />' + cal.formatmonth(date_next.year,
                                                                                          date_next.month, ))
        return context

    def get_queryset(self):
        qry = super(DataImportView, self).get_queryset()
        qry = qry.filter(journey__dataownercode=self.request.user.userprofile.company)
        qry = qry.values('date').annotate(dcount=Count('date')).order_by('date')
        return qry


class StopLineSearchView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Line
    render_object = 'object'

    def get_object(self, **kwargs):
        qry = self.get_queryset()
        return qry

    def get_queryset(self):
        lijnen = self.request.GET.get('lijnen', None)[0:-1].split(',')
        stops = self.request.GET.get('stops', None)[0:-1].split(',')
        if lijnen is None or stops is None:
            return
        dataownercode = stops[0].split('_')[0]
        line_stops = {}
        used_stops = []
        if 'None' in lijnen[0]:
            line_stops[lijnen[0]] = stops
        else:
            for line in lijnen:
                if line == 'Onbekend':
                    continue
                line_stops[line] = []
                query = Kv1Line.objects.filter(dataownercode=dataownercode, lineplanningnumber=line)
                stop_map = query.values('stop_map')[0]['stop_map']
                for stop in stops:
                    if stop in stop_map:
                        line_stops[line].append(stop)
                        if stop not in used_stops:
                            used_stops.append(stop)
            # check if all stops are 'used'
            extra_stops = []
            for stop in stops:
                if stop not in used_stops:
                    extra_stops.append(stop)
            if len(extra_stops) > 0:
                line_stops['x/Onbekend'] = extra_stops
        return line_stops
