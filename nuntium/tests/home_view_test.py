from global_test_case import GlobalTestCase as TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from popit.models import ApiInstance
from nuntium.models import WriteItInstance

class HomeViewTestCase(TestCase):
    def setUp(self):
        super(HomeViewTestCase,self).setUp()

        
    def test_it_is_reachable(self):
        url = reverse("home")
        response = self.client.get(url)

        self.assertTemplateUsed(response, "home.html")
        self.assertEquals(response.status_code,200)


    def test_it_translates_correctly(self):
        activate('es')
        url = reverse("home")
        self.assertTrue("/es/" in url)

    def test_list_instances(self):
        api_instance1 = ApiInstance.objects.all()[0]
        instance1 = WriteItInstance.objects.all()[0]
        url = reverse("home")
        response = self.client.get(url)
        self.assertEquals(response.status_code,200)
        self.assertTrue(response.context['writeitinstances'])
        self.assertEquals(response.context['writeitinstances'].count(),2)
        self.assertEquals(response.context['writeitinstances'][0],instance1)
        
