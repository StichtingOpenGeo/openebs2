from django.views.generic import TemplateView
from utils.views import AccessMixin


class DashboardView(AccessMixin, TemplateView):
    permission_required = 'bigdata.view_dashboard'
    template_name = "bigdata/dashboard.html"
