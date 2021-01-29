from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from openebs.models import Kv1StopFilter, Kv1StopFilterStop
from utils.views import AccessMixin


class FilterListView(AccessMixin, ListView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter


class FilterCreateView(AccessMixin, CreateView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter
    success_url = reverse_lazy('filter_list')
    fields = ['name']


# TODO: Make this JSON
class FilterStopCreateView(AccessMixin, CreateView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilterStop
    success_url = reverse_lazy('filter_list')
    fields = ['filter', 'stop']


# TODO: Make this JSON
class FilterStopDeleteView(AccessMixin, DeleteView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilterStop
    success_url = reverse_lazy('filter_list')


class FilterDeleteView(AccessMixin, DeleteView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter
    success_url = reverse_lazy('filter_list')


class FilterUpdateView(AccessMixin, UpdateView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter
    fields = ['name']

    def get_success_url(self):
        return reverse_lazy('filter_edit', args=(self.object.id, ))
