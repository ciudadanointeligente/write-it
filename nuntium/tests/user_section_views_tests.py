from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse, get_domain
from django.core.urlresolvers import reverse as original_reverse
from nuntium.models import WriteItInstance
from django.contrib.auth.models import User
from django.test.client import Client
from django.test.client import RequestFactory
from nuntium.views import WriteItInstanceUpdateView
from django.forms import ModelForm
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import activate


urlconf = settings.SUBDOMAIN_URLCONFS.get(None, settings.ROOT_URLCONF)

class UserSectionTestCase(TestCase):
    def setUp(self):
        super(UserSectionTestCase, self).setUp()
        self.user = User.objects.create_user(username="fiera", email="fiera@votainteligente.cl", password="feroz")

    # This test should assert that a response redirects to the login interface
    # and if given a certain next_url then it also tests that
    # rigth after login it should go to that url
    def assertRedirectToLogin(self, response, next_url=None):

        self.assertEquals(response.status_code, 302)
        #when redirecting it always returns the full url based on test server so 
        #in order to compare it I'll remove the testserver from the url
        location_this_response_is_taking_us_to = response['Location'].replace("http://testserver","")
        #the login url comes with the localized url
        #So I'll set it to english and then remove it from the url
        activate('en')
        login_url = original_reverse('django.contrib.auth.views.login', urlconf=urlconf).replace('/en','')
        self.assertTrue(location_this_response_is_taking_us_to.startswith(login_url))
        if next_url:
            current_domain = "http://" + Site.objects.get_current().domain
            next_url = next_url.replace(current_domain, "")
            self.assertTrue(location_this_response_is_taking_us_to.endswith("?next="+next_url))


class UserViewTestCase(UserSectionTestCase):

    def test_account_url_exists(self):
        url = reverse('account')

        self.assertTrue(url)

    def test_the_url_is_not_reachable_when_not_logged(self):
        c = Client()
        url = reverse('account')
        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)


    def test_the_url_exists_and_is_reachable_when_logged(self):
        c = Client()
        c.login(username='fiera', password='feroz')
        url = reverse('account')
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "nuntium/user_account.html")
        self.assertTemplateUsed(response, "base.html")


class WriteitInstanceUpdateTestCase(UserSectionTestCase):
    def setUp(self):
        super(WriteitInstanceUpdateTestCase, self).setUp()
        self.factory = RequestFactory()
        self.writeitinstance = WriteItInstance.objects.all()[0]


    def test_writeit_instance_edit_url_exists(self):
        url = reverse('writeitinstance_update', kwargs={'pk':self.writeitinstance.pk})

        self.assertTrue(url)

    def test_update_view(self):
        url = reverse('writeitinstance_update', kwargs={'pk':self.writeitinstance.pk})
        request = self.factory.get(url)
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
        self.assertRedirectToLogin(response, next_url=url)



