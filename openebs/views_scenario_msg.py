from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.edit import BaseFormView
from openebs.models import Kv15Scenario

__author__ = 'joel'


class ScenarioContentMixin(BaseFormView):
    """  Overide a few defaults used by scenario messages  """
    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(ScenarioContentMixin, self).get_context_data(**kwargs)
        if self.kwargs.get('scenario', None):
            data['scenario'] = get_object_or_404(Kv15Scenario, pk=self.kwargs.get('scenario', None),
                                                        dataownercode=self.request.user.userprofile.company)
        return data

    def get_success_url(self):
        if self.kwargs.get('scenario', None):
            return reverse_lazy('scenario_edit', args=[self.kwargs.get('scenario')])
        else:
            return reverse_lazy('scenario_index')