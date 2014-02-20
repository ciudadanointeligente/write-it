from django.test import TestCase
from django.utils.unittest import skipUnless
from django.core.management import call_command
from tastypie.test import ResourceTestCase
from django.conf import settings
from django.contrib.sites.models import Site
from popit.tests import instance_helpers
import os
import subprocess
import threading
from django.db import DEFAULT_DB_ALIAS

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

def popit_load_data(fixture_name='default'):

    """
    Use the mongofixtures CLI tool provided by the pow-mongodb-fixtures package
    used by popit-api to load some test data into db. Don't use the test fixture
    from popit-api though as we don't want changes to that to break our test
    suite.

        https://github.com/powmedia/pow-mongodb-fixtures#cli-usage

    """
    instance_helpers.delete_api_database()
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__)))
    
    # gather the args for the call
    mongofixtures_path = os.path.join( project_root, 'popit-api-for-testing/node_modules/.bin/mongofixtures' )
    database_name      = instance_helpers.get_api_database_name()
    test_fixtures_path = os.path.join( project_root, 'nuntium/tests/fixtures/%s.js'%fixture_name )

    # Check that the fixture exists
    if not os.path.exists(test_fixtures_path):
        raise Exception("Could not find fixture for %s at %s" % (fixture_name, test_fixtures_path))

    # Hack to deal with bad handling of absolute paths in mongofixtures.
    # Fix: https://github.com/powmedia/pow-mongodb-fixtures/pull/14
    test_fixtures_path = os.path.relpath( test_fixtures_path )

    # Usage: mongofixtures db_name path/to/fixtures.js
    dev_null = open(os.devnull, 'w')
    exit_code = subprocess.call([mongofixtures_path, database_name, test_fixtures_path], stdout=dev_null)
    if exit_code:
        raise Exception("Error loading fixtures for '%s'" % fixture_name)   

class WriteItTestCaseMixin(object):
    fixtures = ['example_data.yaml']
    def setUp(self):
        self.site = Site.objects.get_current()

    def assertModerationMailSent(self, message, moderation_mail):
        self.assertEquals(moderation_mail.to[0], message.writeitinstance.owner.email)
        self.assertTrue(message.content in moderation_mail.body)
        self.assertTrue(message.subject in moderation_mail.body)
        self.assertTrue(message.author_name in moderation_mail.body)
        self.assertTrue(message.author_email in moderation_mail.body)
        expected_from_email = message.writeitinstance.slug+"@"+settings.DEFAULT_FROM_DOMAIN
        self.assertEquals(moderation_mail.from_email, expected_from_email)
        for person in message.people:
            self.assertTrue(person.name in moderation_mail.body)



class GlobalTestCase(WriteItTestCaseMixin, TestCase):
    pass


class ResourceGlobalTestCase(WriteItTestCaseMixin ,ResourceTestCase ):
    pass

@skipUnless(settings.LOCAL_ELASTICSEARCH, "No local elasticsearch")
class SearchIndexTestCase(GlobalTestCase):
    def setUp(self):
        super(SearchIndexTestCase, self).setUp()
        call_command('rebuild_index', verbosity=0, interactive = False)
    