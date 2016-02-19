from django.views.generic import TemplateView

from kv1.models import Kv1Line
from openebs.views_generic import TemplateRequestView
from utils.views import AccessMixin


class FerryHomeView(AccessMixin, TemplateRequestView):
    template_name = "ferry/ferry_home.html"
    permission_required = 'openebs.add_messages'

    def get_context_data(self, **kwargs):
        ctx = super(FerryHomeView, self).get_context_data(**kwargs)
        ctx['lines'] = Kv1Line.objects.filter(is_ferry=True, dataownercode=self.request.user.userprofile.company)
        return ctx