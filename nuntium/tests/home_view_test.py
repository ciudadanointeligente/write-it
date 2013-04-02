from django.test import TestCase
from django.core.urlresolvers import reverse

class HomeViewTestCase(TestCase):
    def test_it_is_reachable(self):
        url = reverse("home")
        response = self.client.get(url)

        self.assertTemplateUsed(response, "home.html")