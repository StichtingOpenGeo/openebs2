from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from utils.views import ExternalMessagePushMixin


#
# Authentication filters
#

class FilterDataownerMixin(SingleObjectMixin):
    # Permission level is used to check which permission is needed by the view. 'read' forces read_only,
    # 'write' allows modifications
    permission_level = None

    def get_queryset(self):
        return filter_user(self.permission_level, self.request.user, super(FilterDataownerMixin, self).get_queryset())


class FilterDataownerListMixin(MultipleObjectMixin):
    # See comment above for usage!
    permission_level = None

    def get_queryset(self):
        return filter_user(self.permission_level, self.request.user, super(FilterDataownerListMixin, self).get_queryset())


def filter_user(perm_level, user, qry):
    if user.userprofile.company is None:
        raise PermissionDenied("Je account is nog niet gelinkt aan een vervoerder")

    if (perm_level == 'read' and not user.has_perm('openebs.view_all')) or \
            (perm_level == 'write' and not user.has_perm('openebs.edit_all')) \
            or perm_level is None:
        qry = qry.filter(dataownercode=user.userprofile.company)

    return qry