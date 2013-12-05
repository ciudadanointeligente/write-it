from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from django.core.urlresolvers import reverse as original_reverse
from nuntium.models import WriteItInstance
from django.contrib.auth.models import User
from django.test.client import Client


class UserViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="fiera", email="fiera@votainteligente.cl", password="feroz")

    def test_account_url_exists(self):
        url = reverse('account')

        self.assertTrue(url)

    def test_the_url_is_not_reachable_when_not_logged(self):
        c = Client()
        url = reverse('account')
        response = c.get(url, follow=True)
        #[TODO] - This test should not be dependent on the url
        self.assertRedirects(response, '/accounts/login/?next=/en/accounts/profile')
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "base.html")


    def test_the_url_exists_and_is_reachable_when_logged(self):
        c = Client()
        c.login(username='fiera', password='feroz')
        url = reverse('account')
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "nuntium/user_account.html")
        self.assertTemplateUsed(response, "base.html")



