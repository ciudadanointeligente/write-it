from global_test_case import GlobalTestCase as TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from ..models import WriteItInstance

from django.test.client import Client


class HomeViewTestCase(TestCase):
    def test_it_is_reachable(self):
        url = reverse("home")

        response = self.client.get(url)
        self.assertTemplateUsed(response, "home.html")
        self.assertEquals(response.status_code, 200)

    def test_it_translates_correctly(self):
        activate('es')
        url = reverse("home")
        self.assertTrue("/es/" in url)

    def test_it_redirects_correctly(self):
        activate('es')
        url = "/"
        response = self.client.get(url)
        self.assertEquals(response.status_code, 301)

        expected_redirection = reverse("home")
        self.assertTrue(response['Location'], expected_redirection)

    def test_list_instances(self):
        activate('en')
        instance1 = WriteItInstance.objects.all()[0]
        url = reverse("home")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['writeitinstances'])
        self.assertEquals(response.context['writeitinstances'].count(), 2)
        self.assertEquals(response.context['writeitinstances'][0], instance1)

    def test_list_instances_view(self):
        url = reverse('instance_list')
        self.assertTrue(url)
        c = Client()
        response = c.get(url)
        self.assertTrue(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIsInstance(response.context['object_list'][0], WriteItInstance)
        self.assertEquals(len(response.context['object_list']), WriteItInstance.objects.count())

        self.assertTemplateUsed(response, 'nuntium/template_list.html')
        self.assertTemplateUsed(response, 'base.html')
