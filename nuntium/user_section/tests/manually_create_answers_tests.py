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
        self.message = self.writeitinstance.message_set.all()[0]

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
        self.assertIn("writeitinstance", response.context)
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance)
        self.assertTemplateUsed(response, "base_edit.html")
        self.assertTemplateUsed(response, "nuntium/profiles/messages_per_instance.html")

    def test_there_is_a_url_to_see_all_answers(self):
        """
        There is a url for getting all answers per message
        """
        url = reverse('answers_per_message', kwargs={'pk':self.writeitinstance.pk})
        self.assertTrue(url)

    def test_get_all_answers_url(self):
        """
        Get the url for all answers per message brings them
        """
        url = reverse('answers_per_message', kwargs={'pk':self.message.pk})
        c = Client()
        c.login(username=self.writeitinstance.owner.username, password='admin')
        response = c.get(url)
        self.assertIn("writeitinstance", response.context)
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance)
        self.assertIn("message", response.context)
        self.assertEquals(response.context['message'], self.message)
        self.assertTemplateUsed(response, "base_edit.html")
        self.assertTemplateUsed(response, "nuntium/profiles/answers_per_message.html")
