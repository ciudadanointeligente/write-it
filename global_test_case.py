import re

from django.test import TestCase
from django.utils.unittest import skipUnless
from django.core.management import call_command
from tastypie.test import ResourceTestCase
from django.conf import settings
from django.contrib.sites.models import Site
import os
import subprocess
import threading
from django.db import DEFAULT_DB_ALIAS
from django.test import RequestFactory
from django.test.client import Client
import logging
from haystack.signals import BaseSignalProcessor

_LOCALS = threading.local()


def set_test_db(db_name):
    "Sets the database name to route to."

    setattr(_LOCALS, 'test_db_name', db_name)


def get_test_db():
    "Get the current database name or the default."

    return getattr(_LOCALS, 'test_db_name', DEFAULT_DB_ALIAS)


def del_test_db():
    "Clear the database name (restore default)"

    try:
        delattr(_LOCALS, 'test_db_name')
    except AttributeError:
        pass


def whitespace_ignoring_in(a, b):
    """Strip all the whitespace from a and b, and then check a in b."""
    def squash(x):
        return re.sub('\s', '', x)

    return squash(a) in squash(b)


class TestUsingDbRouter(object):
    "Simple router to allow DB selection by name."

    def db_for_read(self, model, **kwargs):
        return get_test_db()

    def db_for_write(self, model, **kwargs):
        return get_test_db()


class UsingDbMixin(object):
    "A mixin to allow a TestCase to select the DB to use."

    multi_db = True
    using_db = None

    def setUp(self, *args, **kwargs):
        super(UsingDbMixin, self).setUp(*args, **kwargs)
        set_test_db(self.using_db)

    def tearDown(self, *args, **kwargs):
        del_test_db()
        super(UsingDbMixin, self).tearDown(*args, **kwargs)


from urlparse import urlparse


def get_path_and_subdomain(path, **extra):
    parsed_uri = urlparse(path)
    # parsed_uri.hostname is None when we say for a request to follow=True
    # and because django.test.Client in the method _handle_redirects(self, response, **extra)
    # does a self.get(url.path, QueryDict(url.query), follow=False, **extra)
    # which cuts the full url but adds the server_name and port to the extra dictionary.
    # We can still override the _handle_redirects in the class WriteItClient
    if parsed_uri.hostname is None:
        full_path = extra['wsgi.url_scheme'] + "://" + extra['SERVER_NAME'] + ":" + extra['SERVER_PORT'] + path
        parsed_uri = urlparse(full_path)
    subdomain = parsed_uri.hostname.split('.')[0]
    domain = parsed_uri.netloc

    if subdomain:
        subdomain = subdomain
        path = path.replace(subdomain + ".", '')
    else:
        subdomain = None
    return path, subdomain, domain


class WriteItRequestFactory(RequestFactory):
    '''
    This is pretty much the same django RequestFactory
    but in order to work with subdomains it returns the same
    request as the SubdomainMiddleware would. In other words
    it determines from the url what the subdomain is.
    '''

    def get(self, path, data={}, secure=False, **extra):
        path, subdomain, domain = get_path_and_subdomain(path, **extra)
        extra.update({
            'SERVER_NAME': str(domain),
            })
        request = super(WriteItRequestFactory, self).get(path, data=data, secure=secure, **extra)
        if subdomain:
            request.subdomain = subdomain
        return request

    def post(self, path, data={}, secure=False, **extra):
        path, subdomain, domain = get_path_and_subdomain(path)
        extra.update({
            'SERVER_NAME': str(domain),
            })
        request = super(WriteItRequestFactory, self).post(path, data=data, secure=secure, **extra)
        if subdomain:
            request.subdomain = subdomain
        return request


class WriteItClient(WriteItRequestFactory, Client):
    pass


class WriteItTestCaseMixin(object):
    client_class = WriteItClient
    fixtures = ['example_data.yaml']

    def setUp(self):
        self.site = Site.objects.get_current()
        self.factory = WriteItRequestFactory()

    def assertRedirects(self, response, expected_url, status_code=302, target_status_code=200, host=None, msg_prefix=''):
        self.assertEquals(response.status_code, status_code)
        self.assertEquals(response.url, expected_url)

    def assertModerationMailSent(self, message, moderation_mail):
        self.assertEquals(moderation_mail.to[0], message.writeitinstance.owner.email)
        self.assertTrue(whitespace_ignoring_in(message.content, moderation_mail.body))
        self.assertTrue(message.subject in moderation_mail.body)
        self.assertTrue(message.author_name in moderation_mail.body)
        self.assertTrue(message.author_email in moderation_mail.body)

        for person in message.people:
            self.assertTrue(person.name in moderation_mail.body)


class GlobalTestCase(WriteItTestCaseMixin, TestCase):
    pass


class ResourceGlobalTestCase(WriteItTestCaseMixin, ResourceTestCase):
    pass


@skipUnless(settings.LOCAL_ELASTICSEARCH, "No local elasticsearch")
class SearchIndexTestCase(GlobalTestCase):
    def setUp(self):
        super(SearchIndexTestCase, self).setUp()
        call_command('rebuild_index', verbosity=0, interactive=False)

from djcelery.contrib.test_runner import CeleryTestSuiteRunner
from django_nose import NoseTestSuiteRunner


class WriteItTestRunner(CeleryTestSuiteRunner, NoseTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):

        # don't show logging messages while testing
        logging.disable(logging.CRITICAL)

        return super(WriteItTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)


class CeleryTestingSignalProcessor(BaseSignalProcessor):
    pass


from vcr import VCR

CASSETTES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              "nuntium/tests/fixtures/vcr_cassettes/")

writeit_vcr = VCR(
    cassette_library_dir=CASSETTES_PATH,
    serializer='json',
    record_mode='once'
)


def popit_load_data(fixture_name='default'):
    func = writeit_vcr.use_cassette(fixture_name + '.yaml')
    return func
