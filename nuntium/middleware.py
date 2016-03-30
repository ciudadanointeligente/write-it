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

        # Django 1.6 doesn't provide a nice way to hook into the language
        # selection process to override it with a default. So instead we add
        # a default language to the session and then remove it again after
        # running 'get_language_from_request'.
        did_override_session_language = False

        if not request.session.get('django_language', None):
            request.session['django_language'] = default_language
            did_override_session_language = True

        language = translation.get_language_from_request(
            request, check_path=check_path)

        if did_override_session_language:
            del request.session['django_language']

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
