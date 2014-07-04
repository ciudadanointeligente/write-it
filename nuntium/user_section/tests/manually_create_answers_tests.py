from global_test_case import GlobalTestCase as TestCase, popit_load_data
from subdomains.utils import reverse, get_domain
from django.core.urlresolvers import reverse as original_reverse
from ...models import WriteItInstance, Membership, \
                      WriteitInstancePopitInstanceRecord, Message
from django.contrib.auth.models import User
from django.test.client import Client, RequestFactory
from ..views import WriteItInstanceUpdateView
from django.forms import ModelForm
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import activate
from ..forms import WriteItInstanceBasicForm, WriteItInstanceAdvancedUpdateForm, \
                    WriteItInstanceCreateForm
from popit.models import Person, ApiInstance
from django.forms.models import model_to_dict
from contactos.models import Contact
from contactos.forms import ContactCreateForm
from ..forms import NewAnswerNotificationTemplateForm, ConfirmationTemplateForm
from mailit.forms import MailitTemplateForm
from django.utils.unittest import skipUnless, skip
from user_section_views_tests import UserSectionTestCase

class ManuallyCreateAnswersTestCase(UserSectionTestCase):

    def setUp(self):
        super(ManuallyCreateAnswersTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]

    def test_there_is_messages_writeit_view(self):
    	'''
    	There is a url for viewing all messages per WriteItInstance
    	'''
    	url = reverse('messages_per_writeitinstance', kwargs={'pk':self.writeitinstance.pk})
    	self.assertTrue(url)


    def test_it_can_be_reached(self):
    	'''
    	The view for viewing messages per writeit instance is reachable
    	'''
    	url = reverse('messages_per_writeitinstance', kwargs={'pk':self.writeitinstance.pk})
    	c = Client()
    	c.login(username=self.writeitinstance.owner.username, password='admin')
    	response = c.get(url)
    	self.assertIn("message_list", response.context)
    	self.assertEquals(self.writeitinstance.message_set.count(), len(response.context['message_list']))
    	self.assertIsInstance(response.context['message_list'][0], Message)
    	self.assertQuerysetEqual(self.writeitinstance.message_set.all(), \
    		[repr(r) for r in response.context['message_list']], ordered=False)
    	self.assertTemplateUsed(response, "base_edit.html")
    	self.assertTemplateUsed(response, "nuntium/profiles/messages_per_instance.html")