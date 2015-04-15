from django.conf import settings


def web_api_settings(request):
    return {'WEB_BASED': settings.WEB_BASED, 'API_BASED': settings.API_BASED}
