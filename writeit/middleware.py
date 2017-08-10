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
        # Unset the subdomain in thread-local storage on the way back
        # up the middleware processing, just before returning the
        # response to the browser.
        self.tls.subdomain = None
        return response
