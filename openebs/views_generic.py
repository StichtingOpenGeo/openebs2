import logging
from braces.views import SuperuserRequiredMixin, LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from kv15.enum import DATAOWNERCODE

log = logging.getLogger('openebs.views.scenario')

class ChangeCompanyView(LoginRequiredMixin, SuperuserRequiredMixin, RedirectView):
    '''
    Allow superusers (and only superusers) to easily change the company they're currently logged in as.
    We use the time before redirect to set the new company
    '''
    permanent = False
    url = reverse_lazy('index')

    def get_redirect_url(self, **kwargs):
        if self.request.user.is_superuser:
            company = self.request.GET.get('company', None)
            if company is not None and company in dict(DATAOWNERCODE):
                log.info("User '%s' (should be a superuser) changed his company from '%s' to '%s'" %
                         (self.request.user, self.request.user.userprofile.company, company))
                self.request.user.userprofile.company = company
                self.request.user.userprofile.save()
        return super(ChangeCompanyView, self).get_redirect_url()

