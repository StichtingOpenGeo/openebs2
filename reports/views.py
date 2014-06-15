# Create your views here.
from datetime import timedelta, datetime, time, date
from django.utils.timezone import now
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView
from reports.models import Kv6Log, SnapshotLog
from utils.views import JSONListResponseMixin, AccessMixin


class VehicleReportView(AccessMixin, TemplateView):
    permission_required = 'reports.view_dashboard'
    template_name = "reports/vehicle_report.html"

    def get_context_data(self, **kwargs):
        data = super(VehicleReportView, self).get_context_data(**kwargs)
        data['list'] = Kv6Log.do_report()
        data['date_today'] = date.today().isoformat()
        return data


class GraphDataView(AccessMixin, JSONListResponseMixin, TemplateView):
    permission_required = 'reports.view_dashboard'
    report_type = 'all'
    period = 'day'
    render_object = 'points'

    def get_context_data(self, **kwargs):
        result = []
        datestring = self.request.GET.get('date', now().date().isoformat()).split('-')
        qrydate = date(int(datestring[0]), int(datestring[1]), int(datestring[2]))

        if self.period == 'day':
            begin = datetime.combine(qrydate, time(2, 0))
            end = datetime.combine(qrydate + timedelta(days=1), time(1, 59))
            key_func = lambda k: k['created'].isoformat()
        elif self.period == 'week':
            begin = datetime.combine(qrydate - timedelta(days=7), time(2, 0))
            end = datetime.combine(qrydate, time(1, 59))
            key_func = lambda k: k['created'].date().isoformat()

        qrydate = [begin, end]
        if self.report_type == 'journeys':
            result = SnapshotLog.do_graph_journeys(qrydate, key_func)
        elif self.report_type == 'vehicles':
            result = SnapshotLog.do_graph_vehicles(qrydate, key_func)

        return {'points': result }

class ActiveVehiclesListView(AccessMixin, GeoJSONLayerView):
    permission_required = 'reports.view_dashboard'
    model = Kv6Log
    geometry_field = 'last_position'
    properties = ['journeynumber', 'vehiclenumber', 'last_punctuality']
    # Filter by active
    queryset = model.objects.filter(last_logged__gte=now()- timedelta(minutes=15)).distinct('vehiclenumber')

