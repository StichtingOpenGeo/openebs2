# Create your views here.
from braces.views import LoginRequiredMixin
from django.utils.timezone import now
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView
from kv1.models import Kv1Line
from reports.models import Kv6Log, SnapshotLog
from utils.views import JSONListResponseMixin, AccessMixin
from datetime import timedelta, date


class VehicleReportView(AccessMixin, TemplateView):
    permission_required = 'openebs.view_dashboard'
    template_name = "reports/vehicle_report.html"

    def get_context_data(self, **kwargs):
        data = super(VehicleReportView, self).get_context_data(**kwargs)
        data['list'] = Kv6Log.do_report()
        return data


class GraphDataView(AccessMixin, JSONListResponseMixin, TemplateView):
    permission_required = 'openebs.view_dashboard'
    render_object = 'points'

    def get_context_data(self, **kwargs):
        datestring = self.request.GET.get('date', now().date().isoformat()).split('-')
        qrydate = date(int(datestring[0]), int(datestring[1]), int(datestring[2]))
        return {'points': SnapshotLog.do_graph(qrydate) }

class ActiveVehiclesListView(AccessMixin, GeoJSONLayerView):
    permission_required = 'openebs.view_dashboard'
    model = Kv6Log
    geometry_field = 'last_position'
    properties = ['journeynumber', 'vehiclenumber', 'last_punctuality']
    # Filter by active
    queryset = model.objects.filter(last_logged__gte=now()- timedelta(minutes=15)).distinct('vehiclenumber')

