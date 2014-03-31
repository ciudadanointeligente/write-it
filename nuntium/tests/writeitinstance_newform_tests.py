# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from subdomains.utils import reverse
from nuntium.models import WriteItInstance, Message, Membership, Confirmation, Moderation
from nuntium.forms import WriteItInstanceCreateFormPopitUrl
from nuntium.views import MessageCreateForm, PerInstanceSearchForm
from contactos.models import Contact, ContactType
from popit.models import ApiInstance, Person
from django.utils.unittest import skipUnless
from datetime import datetime
from django.contrib.auth.models import User
from subdomains.tests import SubdomainTestMixin
from django.utils.translation import activate
from django.utils.translation import ugettext as _
from django.conf import settings

class InstanceCreateFormTestCase(TestCase):
    def setUp(self):
        super(InstanceCreateFormTestCase, self).setUp()
        self.user = User.objects.first()

    def test_instanciate_the_form(self):
        data = {
            'owner' : self.user.id ,
            'popit_url' : settings.TEST_POPIT_API_URL, 
            'name' : "instance"
            }
        form = WriteItInstanceCreateFormPopitUrl(data)

        self.assertTrue(form)
        self.assertTrue(form.is_valid())

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_creating_an_instance(self):
        # We have a popit running locally using the 
        # start_local_popit_api.bash script
        popit_load_data()
        #loading data into the popit-api

        data = {
            'owner' : self.user.id ,
            'popit_url' : settings.TEST_POPIT_API_URL, 
            'name' : "instance"
            }
        form = WriteItInstanceCreateFormPopitUrl(data)
        instance = form.save()
        self.assertTrue(instance.persons.all())