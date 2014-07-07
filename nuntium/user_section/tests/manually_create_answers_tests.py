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
        self.message = self.writeitinstance.message_set.all()[1]

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

    def test_the_messages_url_is_not_reachable_by_non_user(self):
        """
        The messages url is not reachable by someone who is not logged in
        """
        url = reverse('messages_per_writeitinstance', kwargs={'pk':self.writeitinstance.pk})
        c = Client()
        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_get_messages_url_by_non_owner(self):
        """
        The url is not reachable if the the user is not the owner
        """
        not_the_owner = User.objects.create_user(username="not_owner", password="secreto")
        url = reverse('messages_per_writeitinstance', kwargs={'pk':self.writeitinstance.pk})
        c = Client()
        c.login(username=not_the_owner.username, password="secreto")
        response = c.get(url)
        self.assertEquals(response.status_code, 404)


    def test_there_is_a_url_to_see_all_answers(self):
        """
        There is a url for getting all answers per message
        """
        url = reverse('message_detail', kwargs={'pk':self.writeitinstance.pk})
        self.assertTrue(url)

    def test_get_all_answers_url(self):
        """
        Get the url for all answers per message brings them
        Is the same as message detail
        """
        url = reverse('message_detail', kwargs={'pk':self.message.pk})
        c = Client()
        c.login(username=self.writeitinstance.owner.username, password='admin')
        response = c.get(url)
        self.assertIn("writeitinstance", response.context)
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance)
        self.assertIn("message", response.context)
        self.assertEquals(response.context['message'], self.message)
        self.assertTemplateUsed(response, "base_edit.html")
        self.assertTemplateUsed(response, "nuntium/profiles/message_detail.html")


    def test_get_answers_per_messages_is_not_reachable_by_non_user(self):
        """
        When a user is not logged in he cannot see the answers per message
        """
        url = reverse('message_detail', kwargs={'pk':self.message.pk})
        c = Client()
        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)


    def test_get_answers_per_message_is_not_reachable_by_non_owner(self):
        """
        When the user not the owner tries to get the answers per message
        he/she is shown a 404 html
        """
        not_the_owner = User.objects.create_user(username="not_owner", password="secreto")

        url = reverse('message_detail', kwargs={'pk':self.message.pk})
        c = Client()
        c.login(username=not_the_owner.username, password="secreto")
        response = c.get(url)
        self.assertEquals(response.status_code, 404)
