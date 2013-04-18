from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from popit.models import ApiInstance
from nuntium.models import WriteItInstance

class HomeViewTestCase(TestCase):
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
        api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        instance1 = WriteItInstance.objects.create(name = 'Instance 1', api_instance= api_instance1, slug='instance-1')
        url = reverse("home")
        response = self.client.get(url)
        self.assertEquals(response.status_code,200)
        self.assertTrue(response.context['writeitinstances'])
        self.assertEquals(response.context['writeitinstances'].count(),1)
        self.assertEquals(response.context['writeitinstances'][0],instance1)
        
