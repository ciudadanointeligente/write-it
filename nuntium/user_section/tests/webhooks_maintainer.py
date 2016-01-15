from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from nuntium.models import WriteItInstance
# from django.forms import ModelForm


class WebhooksMaintainerTestCase(TestCase):
    def setUp(self):
        super(WebhooksMaintainerTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]

    def test_the_url_is_reachable_and_contains_previously_created_webhooks(self):
        '''There is a url that lists all previously created webhooks'''

        url = reverse('writeitinstance_webhooks', subdomain=self.writeitinstance.slug)
        self.assertTrue(url)
        c = self.client
        c.login(username=self.writeitinstance.owner.username, password='admin')

        response = c.get(url)
        self.assertTemplateUsed(response, "nuntium/profiles/webhooks.html")
        # self.assertIn('form', response.context)
        # form = response.context['form']

        # self.assertIsInstance(form, ModelForm)
