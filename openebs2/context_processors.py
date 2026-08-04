from django.conf import settings


def social_login(request):
    return {'SOCIAL_LOGIN_ENABLED': settings.SOCIAL_LOGIN_ENABLED}
