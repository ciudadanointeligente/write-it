import threading

class SubdomainInThreadLocalStorageMiddleware(object):

    tls = threading.local()

    def process_request(self, request):
        # Set the subdomain in thread-local storage, so that we can
        # use it in a custom template loader.
        if hasattr(request, 'subdomain'):
            self.tls.subdomain = request.subdomain
        else:
            self.tls.subdomain = None

    def process_response(self, request, response):
        # Remove the subdomain attribute from thread-local storage on
        # the way back up the middleware processing, just before
        # returning the response to the browser. This looks like it
        # shouldn't make any difference (since the subdomain attribute
        # is created again on each process_request) but in fact it
        # does for tests: if the subdomain attribute still exists in
        # the thread-local storage, tests that use templates outside
        # of HTTP requests might pass when they should fail.
        try:
            delattr(self.tls, 'subdomain')
        except AttributeError:
            pass
        return response
