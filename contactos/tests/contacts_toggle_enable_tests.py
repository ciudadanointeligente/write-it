from nuntium.user_section.tests.user_section_views_tests import UserSectionTestCase
from django.contrib.auth.models import User
from contactos.models import Contact
from subdomains.utils import reverse
import json
from django.core import mail


class TogleEnableDisableContact(UserSectionTestCase):
    def setUp(self):
        super(TogleEnableDisableContact, self).setUp()
        self.user = User.objects.get(id=1)
        self.writeitinstance = self.user.writeitinstances.get(id=2)
        self.user.set_password('fiera')
        self.user.save()

        self.contact = Contact.objects.get(id=1)
        self.contact.writeitinstance = self.writeitinstance
        self.contact.save()

    def test_get_the_url(self):
        '''Getting a url for toggle enabled a contact'''
        url = reverse('toggle-enabled', subdomain=self.writeitinstance.slug)

        self.assertTrue(url)

    def test_post_to_the_url(self):
        '''
        By posting to toggle-enabled you
        can toggle enabled or disabled a contact
        '''

        url = reverse('toggle-enabled', subdomain=self.writeitinstance.slug)
        self.client.login(username=self.user.username, password='fiera')
        response = self.client.post(url, data={'id': self.contact.pk})
        self.assertEquals(response.status_code, 200)
        contact = Contact.objects.get(id=self.contact.id)
        self.assertFalse(contact.enabled)

    def test_post_result_content(self):
        '''When posting we the response contains the contact id and the status'''
        url = reverse('toggle-enabled', subdomain=self.writeitinstance.slug)
        self.client.login(username=self.user.username, password='fiera')
        response = self.client.post(url, data={'id': self.contact.pk})

        json_answer = json.loads(response.content)
        self.assertIn('contact', json_answer.keys())
        self.assertEquals(json_answer['contact']['id'], self.contact.pk)
        self.assertFalse(json_answer['contact']['enabled'])

        response = self.client.post(url, data={'id': self.contact.pk})
        json_answer = json.loads(response.content)
        self.assertTrue(json_answer['contact']['enabled'])

    def test_only_owner_of_instance_can_change_status(self):
        '''Only the owner of the instances contact can toggle enabled'''
        url = reverse('toggle-enabled', subdomain=self.writeitinstance.slug)
        response = self.client.post(url, data={'id': self.contact.pk})

        self.assertRedirectToLogin(response)

    def test_if_not_user_it_returns_404(self):
        '''If a user that is not owner tries to post returns 404'''
        url = reverse('toggle-enabled', subdomain=self.writeitinstance.slug)
        User.objects.create_user(username="not_owner", password="123456")
        self.client.login(username="not_owner", password="123456")
        response = self.client.post(url, data={'id': self.contact.pk})
        self.assertEquals(response.status_code, 404)

    def test_it_does_not_try_to_send_emails_when_saving(self):
        '''It does not send emails when saving'''
        url = reverse('toggle-enabled', subdomain=self.writeitinstance.slug)
        self.client.login(username=self.user.username, password='fiera')
        response = self.client.post(url, data={'id': self.contact.pk})
        self.assertEquals(response.status_code, 200)
        contact = Contact.objects.get(id=self.contact.id)
        self.assertFalse(contact.is_bounced)
        self.assertEquals(len(mail.outbox), 0)
