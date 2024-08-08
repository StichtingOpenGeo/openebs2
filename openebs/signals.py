from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from django.contrib.auth.models import Permission

from openebs.models import UserProfile


@receiver(user_logged_in)
def user_logged_in_signal_handler(request, user, **kwargs):
    social_account = SocialAccount.objects.get(user=request.user)
    roles = social_account.extra_data.get('realm_access', {}).get('roles', [])

    permission_set = []
    if 'KV15' in roles:
        permission_set += list(Permission.objects.filter(codename__in=['view_messages', 'add_messages']))
    else:
        permission_set += list(Permission.objects.filter(codename__in=['view_messages']))

    if 'KV17' in roles:
        permission_set += list(Permission.objects.filter(codename__in=['view_change', 'add_change', 'cancel_lines', 'cancel_alllines', 'view_scenario', 'add_scenario']))
    else:
        permission_set += list(Permission.objects.filter(codename__in=['view_change', 'view_scenario']))

    suffix = user.email.split('@')[-1]
    if suffix == 'htm.nl':
        UserProfile.objects.update_or_create(user=user, company='HTM')

    user.user_permissions.set(permission_set)

    user.save()
