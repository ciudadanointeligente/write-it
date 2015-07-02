import os

from django.conf import settings

class SubdomainTemplateOverrideMiddleware(object):
    """
    This middleware manipulates settings.TEMPLATE_DIRS to allow
    subdomain-specific templates to override the global templates.

    Override templates must be placed within directories named after the
    subdomain they apply to, within a 'subdomains' directory in any of the
    paths in settings.TEMPLATE_DIRS.

    For example:
    To use a custom 'about.html' template for subdomain1.example.org,
    create your updated about.html in writeit/templates/subdomains/subdomain1/

    This middleware is intended to be used with django-subdomains, and
    must appear after subdomains.middleware.SubdomainURLRoutingMiddleware.
    """
    def process_request(self, request):
        if hasattr(request, 'subdomain') and request.subdomain is not None:
            request.OLD_TEMPLATE_DIRS = settings.TEMPLATE_DIRS
            new_template_dirs = list(settings.TEMPLATE_DIRS)
            for template_dir in settings.TEMPLATE_DIRS:
                subdomain_dir = os.path.join(template_dir, "subdomains", request.subdomain)
                if os.path.isdir(subdomain_dir):
                    new_template_dirs.insert(0, subdomain_dir)
            settings.TEMPLATE_DIRS = new_template_dirs

    def process_response(self, request, response):
        if hasattr(request, 'OLD_TEMPLATE_DIRS'):
            settings.TEMPLATE_DIRS = request.OLD_TEMPLATE_DIRS
            del(request.OLD_TEMPLATE_DIRS)
        return response
