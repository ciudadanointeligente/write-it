from collections import OrderedDict

from django.middleware.locale import LocaleMiddleware
from django.utils import translation
from django.conf import settings

from nuntium.models import WriteItInstanceConfig


def get_language_from_request(request, check_path=False):
    if check_path:
        lang_code = translation.get_language_from_path(request.path_info)
        if lang_code is not None:
            return lang_code

    try:
        lang_code = WriteItInstanceConfig.objects.get(writeitinstance__slug=request.subdomain).default_language
    except WriteItInstanceConfig.DoesNotExist:
        lang_code = None

    if lang_code is not None and translation.check_for_language(lang_code):
        return lang_code

    # Call with check_path False as we've already done that above!
    return translation.get_language_from_request(request, check_path=False)


class InstanceLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        """Same as parent, except calling our own get_language_from_request"""
        check_path = self.is_language_prefix_patterns_used()
        language = get_language_from_request(request, check_path=check_path)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
