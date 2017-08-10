from django.core.exceptions import SuspiciousFileOperation
from django.template.loaders.filesystem import Loader
from django.utils._os import safe_join

from .middleware import SubdomainInThreadLocalStorageMiddleware


class SubdomainFilesystemLoader(Loader):

    # This implementation is the same as that in the filesystem loader
    # in core Django that we're overriding, except for inserting the
    # subdomain-specific subdirectory into the template path that will
    # be tried. If no subdomain is specified, this does nothing.

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs" followed by the 'subdomains/<subdomain>'.
        Any paths that don't lie inside one of the template dirs are excluded
        from the result set, for security reasons.
        """
        subdomain = SubdomainInThreadLocalStorageMiddleware.tls.subdomain
        if not subdomain:
            return
        if not template_dirs:
            template_dirs = self.engine.dirs
        for template_dir in template_dirs:
            try:
                yield safe_join(template_dir, 'subdomains', subdomain, template_name)
            except SuspiciousFileOperation:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                pass
