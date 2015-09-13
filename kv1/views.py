from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from datetime import timedelta
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from djgeojson.views import GeoJSONLayerView
from openebs.models import Kv15Stopmessage
from utils.calender import CountCalendar
from utils.time import get_operator_date
from utils.views import JSONListResponseMixin
from kv1.models import Kv1Line, Kv1Stop, Kv1Journey, Kv1JourneyDate


class LineSearchView(LoginRequiredMixin, JSONListResponseMixin, ListView):
    model = Kv1Line
    render_object = 'object_list'

    def get_queryset(self):
        qry = super(LineSearchView, self).get_queryset()
        qry = qry.filter(dataownercode=self.request.user.userprofile.company) \
            .order_by('lineplanningnumber') \
            .values('pk', 'dataownercode', 'headsign', 'lineplanningnumber', 'publiclinenumber')
        needle = unicode(self.kwargs.get('search', '') or '')
        qry = qry.filter(Q(headsign__icontains=needle) | Q(publiclinenumber__startswith=needle))
        return qry

class LineStopView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Line
    render_object = 'object'

    def get_object(self, queryset=None):
        '''
        This is a bit of a hack, but forces our JSON we get out of the db out as JSON again
        '''
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk', None))
        if obj:
            return { 'stop_map' : obj.stop_map }
        return obj

class LineTripView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Line
    render_object = 'object'

    def get_object(self, queryset=None):
        '''
        Forces our output as json and do some queries
        '''
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk', None))
        if obj:
            # Note, the list() is required to serialize correctly
            # We're filtering on todays trips #
            journeys = obj.journeys.filter(dates__date=get_operator_date()).order_by('departuretime')\
                                   .values('id', 'journeynumber', 'direction', 'departuretime')
            return { 'trips_1' : list(journeys.filter(direction=1)), 'trips_2' : list(journeys.filter(direction=2)) }
        return obj

class ActiveStopListView(LoginRequiredMixin, GeoJSONLayerView):
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode', 'timingpointcode']
    # Filter by active
    queryset = model.objects.filter(messages__stopmessage__messagestarttime__lte=now(),
                                    messages__stopmessage__messageendtime__gte=now(),
                                    messages__stopmessage__isdeleted=False).exclude(timingpointcode=0).distinct('timingpointcode')

    def get_queryset(self):
        qry = super(ActiveStopListView, self).get_queryset()
        if not self.request.user.has_perm("openebs.view_all"):
            qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        return qry

class ActiveMessagesForStopView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
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
        return qry.values('dataownercode', 'kv15stopmessage__messagecodenumber', 'kv15stopmessage__messagecodedate',
                          'kv15stopmessage__messagecontent', 'kv15stopmessage__id', 'messages__stopmessage__messagestarttime',
                          'messages__stopmessage__messageendtime')

    def get_object(self):
        # Note, can't set this on the view, because it triggers the queryset cache
        return list(self.get_queryset())


class DataImportView(LoginRequiredMixin, StaffuserRequiredMixin, ListView):
    '''
    Show details about what data was or wasn't imported
    '''
    model = Kv1JourneyDate
    template_name = 'kv1/importdata_list.html'

    def get_context_data(self, **kwargs):
        context = super(DataImportView, self).get_context_data(**kwargs)
        cal = CountCalendar(context['object_list'])
        context['calendar'] = mark_safe(cal.formatmonth(2014, 1)+'<br />'+cal.formatmonth(2014, 2))
        return context

    def get_queryset(self):
        qry = super(DataImportView, self).get_queryset()
        qry = qry.filter(journey__dataownercode=self.request.user.userprofile.company)
        qry = qry.values('date').annotate(dcount=Count('date')).order_by('date')
        return qry