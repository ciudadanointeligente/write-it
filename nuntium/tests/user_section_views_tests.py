from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from django.core.urlresolvers import reverse as original_reverse
from nuntium.models import WriteItInstance
from django.contrib.auth.models import User
from django.test.client import Client
from django.test.client import RequestFactory
from nuntium.views import WriteItInstanceUpdateView
from django.forms import ModelForm

class UserViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="fiera", email="fiera@votainteligente.cl", password="feroz")

    def test_account_url_exists(self):
        url = reverse('account')

        self.assertTrue(url)

    ## Need to improve this test now I have to GO!
    def test_the_url_is_not_reachable_when_not_logged(self):
        c = Client()
        url = reverse('account')
        response = c.get(url, follow=True)
        #[TODO] - This test should not be dependent on the url
        self.assertRedirects(response, '/en/accounts/login/?next=%2Fen%2Faccounts%2Fprofile')
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


class WriteitInstanceUpdateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="fiera", email="fiera@votainteligente.cl", password="feroz")
        self.writeitinstance = WriteItInstance.objects.all()[0]


    def test_writeit_instance_edit_url_exists(self):
        url = reverse('writeitinstance_update', kwargs={'pk':self.writeitinstance.pk})

        self.assertTrue(url)

    def test_update_view(self):
        request = self.factory.get('/customer/details')
        request.user = self.user

        view = WriteItInstanceUpdateView()
        form = view.get_form_class()
        self.assertEquals(form._meta.model, WriteItInstance)
        self.assertEquals(view.fields, ["name","persons",])
        self.assertEquals(view.template_name_suffix, '_update_form')

    def test_update_view_is_not_reachable_by_a_non_user(self):
        url = reverse('writeitinstance_update', kwargs={'pk':self.writeitinstance.pk})
        client = Client()
        response = client.get(url)
        self.assertEquals(response.status_code, 302) #is redirected



