from braces.views import JSONResponseMixin, LoginRequiredMixin
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from djgeojson.views import GeoJSONLayerView
from kv1.models import Kv1Line, Kv1Stop

# TODO Refactor this to be an proper view based off some other model class
class JSONListResponseMixin(JSONResponseMixin):
    render_object = None #Name of thing to get from context object

    def render_to_response(self, context):
        contents = {}
        if self.render_object:
            if isinstance(context[self.render_object], QuerySet):
                contents[self.render_object] = list(context[self.render_object])
            else:
                contents[self.render_object] = context[self.render_object]
        return self.render_json_response(contents)

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

class ActiveStopListView(GeoJSONLayerView):
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode', 'messages']
    # Filter by active
    # queryset = model.objects.filter(messages__stopmessage__messagestarttime__lt=now,
    #                                 messages__stopmessage__messageendtime__gt=now)

    def get_queryset(self):
        qry = super(ActiveStopListView, self).get_queryset()
        qry = qry.filter(dataownercode=self.request.user.userprofile.company)
        return qry


