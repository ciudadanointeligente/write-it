from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import activate

class HomeViewTestCase(TestCase):
    def test_it_is_reachable(self):
        url = reverse("home")
        response = self.client.get(url)

        self.assertTemplateUsed(response, "home.html")


    def test_it_translates_correctly(self):
        activate('es_CL')
        url = reverse("home")

        self.assertEquals(url, "/es-cl/")

