from subdomains.utils import reverse
from instance.models import WriteItInstance
from nuntium.user_section.forms import WebhookCreateForm
from nuntium.models import AnswerWebHook
from django.contrib.auth.models import User
from nuntium.user_section.tests.user_section_views_tests import UserSectionTestCase


class WebhooksMaintainerTestCase(UserSectionTestCase):
    def setUp(self):
        super(WebhooksMaintainerTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.writeitinstance.answer_webhooks.all().delete()

    def test_create_a_new_webhook_form(self):
        data = {
            'url': "http://new.answers.will.be.posted/here"
        }
        form = WebhookCreateForm(data=data, writeitinstance=self.writeitinstance)
        self.assertTrue(form.is_valid())
        webhook = form.save()
        self.assertIsInstance(webhook, AnswerWebHook)
        self.assertEquals(webhook.writeitinstance, self.writeitinstance)
        self.assertEquals(webhook.url, data['url'])

    def test_the_url_is_reachable_and_contains_previously_created_webhooks(self):
        '''There is a url that lists all previously created webhooks'''

        url = reverse('writeitinstance_webhooks', subdomain=self.writeitinstance.slug)
        c = self.client
        c.login(username=self.writeitinstance.owner.username, password='admin')

        response = c.get(url)
        self.assertTemplateUsed(response, "nuntium/profiles/webhooks.html")
        self.assertIn('form', response.context)
        form = response.context['form']

        self.assertIsInstance(form, WebhookCreateForm)
        self.assertEquals(form.writeitinstance, self.writeitinstance)

    def test_there_is_a_url_for_posting_new_webhooks(self):
        '''There is a url where we can post information for a new webhook'''
        url = reverse('writeitinstance_create_webhooks', subdomain=self.writeitinstance.slug)
        self.client.login(username=self.writeitinstance.owner.username, password='admin')
        data = {'url': 'http://new.answers.will.be.posted/here'}
        response = self.client.post(url, data=data)
        url_listing_webhooks = reverse('writeitinstance_webhooks', subdomain=self.writeitinstance.slug)
        self.assertRedirects(response, url_listing_webhooks)
        webhook = self.writeitinstance.answer_webhooks.first()
        self.assertEquals(webhook.url, data['url'])

    def test_webhook_listing_security(self):
        '''Basic security for listing webhooks'''
        url = reverse('writeitinstance_create_webhooks', subdomain=self.writeitinstance.slug)
        response = self.client.get(url)
        self.assertRedirectToLogin(response)
        otheruser = User.objects.create_user(username="otheruser", password='passw')
        self.client.login(username=otheruser.username, password='passw')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_webhook_creation_security(self):
        '''Basic security for creating webhooks'''
        url = reverse('writeitinstance_create_webhooks', subdomain=self.writeitinstance.slug)
        data = {'url': 'http://new.answers.will.be.posted/here'}
        self.client.post(url, data=data)
        self.assertFalse(self.writeitinstance.answer_webhooks.all())

        otheruser = User.objects.create_user(username="otheruser", password='passw')
        self.client.login(username=otheruser.username, password='passw')
        self.client.post(url, data=data)
        self.assertFalse(self.writeitinstance.answer_webhooks.all())
