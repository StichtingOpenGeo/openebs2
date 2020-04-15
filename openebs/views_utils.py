from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from datetime import datetime
from django.utils.timezone import make_aware


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


def datetime_32h(operatingday, begintime):
    if begintime is None:
        return None
    else:
        operatingday_time = make_aware(datetime.combine(operatingday, datetime.min.time()))
        begintime_diff = begintime - operatingday_time
        hours = begintime_diff.days * 24 + (begintime_diff.seconds / 3600)
        minutes = (begintime_diff.seconds % 3600) / 60
        seconds = begintime_diff.seconds % 60
        return '%02d:%02d:%02d' % (hours, minutes, seconds)