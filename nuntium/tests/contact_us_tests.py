from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from django.contrib.auth.models import User


class ContactUsTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_the_contact_us_url(self):
        user = User.objects.get(id=1)
        url = reverse('contact_us', subdomain=None)
        self.client.login(username=user.username, password='admin')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/profiles/contact.html')
