from braces.views import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from djgeojson.views import GeoJSONLayerView
from utils.views import JSONListResponseMixin
from kv1.models import Kv1Line, Kv1Stop

class LineSearchView(LoginRequiredMixin, JSONListResponseMixin, ListView):
    model = Kv1Line
    render_object = 'object_list'

    def get_queryset(self):
        qry = super(LineSearchView, self).get_queryset()
        qry = qry.filter(dataownercode=self.request.user.userprofile.company) \
            .order_by('lineplanningnumber') \
            .values('pk', 'dataownercode', 'headsign', 'lineplanningnumber')
        if self.kwargs['search']:
            pass
        qry = qry.filter(Q(headsign__icontains=self.kwargs['search']) | Q(lineplanningnumber__startswith=self.kwargs['search']))
        return qry

class LineShowView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
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

class ActiveStopListView(LoginRequiredMixin, GeoJSONLayerView):
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode', 'messages']
    # Filter by active
    queryset = model.objects.filter(messages__stopmessage__messagestarttime__lt=now,
                                    messages__stopmessage__messageendtime__gt=now)

    def get_queryset(self):
        qry = super(ActiveStopListView, self).get_queryset()
        qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        return qry


