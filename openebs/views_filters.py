from braces.views import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from openebs.models import Kv1StopFilter, Kv1StopFilterStop


class FilterListView(LoginRequiredMixin, ListView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter


class FilterCreateView(LoginRequiredMixin, CreateView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter
    success_url = reverse_lazy('filter_list')
    fields = ['name']


# TODO: Make this JSON
class FilterStopCreateView(LoginRequiredMixin, CreateView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilterStop
    success_url = reverse_lazy('filter_list')
    fields = ['filter', 'stop']


# TODO: Make this JSON
class FilterStopDeleteView(LoginRequiredMixin, DeleteView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilterStop
    success_url = reverse_lazy('filter_list')


class FilterDeleteView(LoginRequiredMixin, DeleteView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter
    success_url = reverse_lazy('filter_list')


class FilterUpdateView(LoginRequiredMixin, UpdateView):
    permission_required = 'openebs.edit_filters'
    model = Kv1StopFilter
    fields = ['name']

    def get_success_url(self):
        return reverse_lazy('filter_edit', args=(self.object.id, ))
