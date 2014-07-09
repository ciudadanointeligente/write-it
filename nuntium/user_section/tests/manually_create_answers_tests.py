from global_test_case import GlobalTestCase as TestCase, popit_load_data
from subdomains.utils import reverse, get_domain
from django.core.urlresolvers import reverse as original_reverse
from ...models import WriteItInstance, Membership, \
                      WriteitInstancePopitInstanceRecord, Message, Answer
from django.contrib.auth.models import User
from django.test.client import Client, RequestFactory
from ..views import WriteItInstanceUpdateView
from django.forms import ModelForm
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import activate
from ..forms import WriteItInstanceBasicForm, WriteItInstanceAdvancedUpdateForm, \
                    WriteItInstanceCreateForm, AnswerForm
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


    def test_there_is_a_form_to_create_an_answer(self):
        '''There is a form to create an answer'''
        # print self.message.people, self.message.writeitinstance.persons.all()
        form = AnswerForm(message=self.message)

        self.assertTrue(form)
        self.assertIn("person", form.fields)
        self.assertIn("content", form.fields)
        self.assertEquals(form.message, self.message)
        self.assertNotIn("message", form.fields)
        self.assertNotIn("created", form.fields)


    def test_only_the_persons_related_to_message(self):
        '''
        Only persons related to the given message are shown in the list
        '''
        
        form = AnswerForm(message=self.message)
        self.assertEquals(len(self.message.people), form.fields['person'].queryset.count())
        self.assertIn(self.message.people[0], form.fields['person'].queryset.all())

    def test_save_an_answer(self):
        '''
        Save an answer with the form
        '''
        data = {
        "person":self.message.people.all()[0].pk,
        "content": "Hello this is an answer"
        }
        form = AnswerForm(data, message=self.message)
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())
        new_answer = form.save()
        self.assertEquals(new_answer.message, self.message)

    def test_there_is_a_create_view_for_an_answer(self):
        '''
        There is a view that I can access to create a message
        '''
        url = reverse('create_answer', kwargs={'pk':self.message.pk})
        self.assertTrue(url)
        c = Client()
        c.login(username=self.writeitinstance.owner.username, password='admin')
        response = c.get(url)
        self.assertEquals(response.status_code, 200)

        self.assertTemplateUsed(response, "nuntium/profiles/create_answer.html")
        self.assertTemplateUsed(response, "base_edit.html")
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEquals(response.context['form'].message, self.message)

    def test_post_to_create_an_answer(self):
        '''
        When posting for the creation of an answer
        '''
        previous_count = Answer.objects.filter(message=self.message).count()
        data = {
        'person': self.message.people.all()[0].pk,
        'content': "hello this is an answer"
        }
        url = reverse('create_answer', kwargs={'pk':self.message.pk})
        self.assertTrue(url)
        c = Client()
        c.login(username=self.writeitinstance.owner.username, password='admin')
        response = c.post(url, data=data)
        detail_message_url = reverse('message_detail', kwargs={'pk':self.message.pk})
        self.assertRedirects(response, detail_message_url)
        new_count = Answer.objects.filter(message=self.message).count()
        self.assertEquals(new_count, previous_count + 1)


    def test_create_answers_not_logged(self):
        '''
        Only owner of a message can create an answer
        '''
        url = reverse('create_answer', kwargs={'pk':self.message.pk})
        c = Client()
        # not logged
        response = c.get(url)
        self.assertRedirectToLogin(response, url)


class DeleteMessageView(UserSectionTestCase):
    def setUp(self):
        super(DeleteMessageView, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.message = self.writeitinstance.message_set.all()[1]


    def test_there_is_a_url_to_delete_messages(self):
        '''There is a url that would help me to delete a message'''
        url = reverse('message_delete', kwargs={'pk':self.message.pk})
        self.assertTrue(url)

    def test_posting_to_that_url_deletes_the_message(self):
        '''When posting to delete a message it deletes it'''
        url = reverse('message_delete', kwargs={'pk':self.message.pk})

        c = Client()
        c.login(username=self.writeitinstance.owner.username, password='admin')
        response = c.post(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Message.objects.filter(id=self.message.id))
        '''It should redirect to the see all messages url'''
        allmessages_url = reverse('messages_per_writeitinstance', kwargs={'pk':self.writeitinstance.pk})
        self.assertRedirects(response, allmessages_url)


    def test_a_get_gives_me_the_cornfirmation_url(self):
        '''When I do a get it takes me to the confirm deleting url'''
        url = reverse('message_delete', kwargs={'pk':self.message.pk})

        c = Client()
        c.login(username=self.writeitinstance.owner.username, password='admin')
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "nuntium/profiles/message_delete_confirm.html")


    def test_it_cannot_be_accessed_by_a_non_user(self):
        '''A non user cannot delete a message'''

        url = reverse('message_delete', kwargs={'pk':self.message.pk})

        c = Client()
        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)


    def test_not_owner_deletes_message(self):
        '''If the user is not the owner of the instance then he/she cannot delete a message'''
        not_the_owner = User.objects.create_user(username="not_owner", password="secreto")

        url = reverse('message_delete', kwargs={'pk':self.message.pk})
        c = Client()
        c.login(username=not_the_owner.username, password="secreto")
        response1 = c.get(url)
        self.assertEquals(response1.status_code, 404)
        response2 = c.post(url)
        self.assertEquals(response2.status_code, 404)
