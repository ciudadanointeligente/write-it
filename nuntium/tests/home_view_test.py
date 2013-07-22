from global_test_case import GlobalTestCase as TestCase
from subdomains.utils import reverse
from django.utils.translation import activate
from popit.models import ApiInstance
from nuntium.models import WriteItInstance
from subdomains.tests import SubdomainTestMixin

class HomeViewTestCase(TestCase, SubdomainTestMixin):
    def setUp(self):
        super(HomeViewTestCase,self).setUp()
        self.host = self.get_host_for_subdomain(None)

        
    def test_it_is_reachable(self):
        url = reverse("home")
        
        response = self.client.get(url, HTTP_HOST=self.host)
        self.assertTemplateUsed(response, "home.html")
        self.assertEquals(response.status_code,200)


    def test_it_translates_correctly(self):
        activate('es')
        url = reverse("home")
        self.assertTrue("/es/" in url)

    def test_it_redirects_correctly(self):
        activate('es')
        url = "/"
        response = self.client.get(url, HTTP_HOST=self.host)

        self.assertEquals(response.status_code, 301)
        expected_redirection = reverse("home")
        self.assertEqual(response['Location'], expected_redirection)


    def test_list_instances(self):
        activate('en')
        api_instance1 = ApiInstance.objects.all()[0]
        instance1 = WriteItInstance.objects.all()[0]
        url = reverse("home")
        response = self.client.get(url, HTTP_HOST=self.host)
        self.assertEquals(response.status_code,200)
        self.assertTrue(response.context['writeitinstances'])
        self.assertEquals(response.context['writeitinstances'].count(),2)
        self.assertEquals(response.context['writeitinstances'][0],instance1)
        
