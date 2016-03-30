from django.middleware.locale import LocaleMiddleware
from django.utils import translation
from django.conf import settings

from nuntium.models import WriteItInstanceConfig


class InstanceLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        check_path = self.is_language_prefix_patterns_used()
        try:
            default_language = WriteItInstanceConfig.objects.get(writeitinstance__slug=request.subdomain).default_language
        except WriteItInstanceConfig.DoesNotExist:
            default_language = settings.LANGUAGE_CODE

        if not request.session.get('django_language', None):
            request.session['django_language'] = default_language
        language = translation.get_language_from_request(
            request, check_path=check_path)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
