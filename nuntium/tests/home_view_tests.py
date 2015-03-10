from global_test_case import GlobalTestCase as TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from ..models import WriteItInstance
from django.contrib.auth.models import User
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
        instance1 = WriteItInstance.objects.get(id=1)
        url = reverse("home")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['writeitinstances'])
        self.assertEquals(response.context['writeitinstances'].count(), 2)
        self.assertEquals(response.context['writeitinstances'][0], instance1)

    def test_list_instances_view(self):
        '''All instances are displayed in home'''
        for instance in WriteItInstance.objects.all():
            instance.config.testing_mode = False
            instance.config.save()
        url = reverse('instance_list')
        self.assertTrue(url)
        c = Client()
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIsInstance(response.context['object_list'][0], WriteItInstance)
        self.assertEquals(len(response.context['object_list']), WriteItInstance.objects.count())

        self.assertTemplateUsed(response, 'nuntium/template_list.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_testing_mode_instances_not_displayed(self):
        '''Test Mode instances are not displayed if a user is not logged in'''
        fiera = User.objects.create_user(username='fiera',
            password="feroz",
            email="fiera@ciudadanointeligente.org")
        w = WriteItInstance.objects.create(name='test_mode_instance', owner=fiera)

        c = Client()
        response = c.get(reverse('instance_list'))
        self.assertEquals(response.status_code, 200)
        self.assertNotIn(w, response.context['object_list'])

    def test_owners_can_see_their_testing_mode_instances(self):
        '''Only the owner can see her/his instances in testing_mode'''
        fiera = User.objects.create_user(username='fiera',
            password="feroz",
            email="fiera@ciudadanointeligente.org")
        benito = User.objects.create_user(username='benito',
            password="feroz",
            email="benito@ciudadanointeligente.org")

        fieras_instance = WriteItInstance.objects.create(name='test_mode_instance',
            owner=fiera)
        benito_instance = WriteItInstance.objects.create(name='test_mode_instance_benito',
            owner=benito)

        c = Client()
        c.login(username='fiera', password="feroz")
        response = c.get(reverse('instance_list'))
        self.assertEquals(response.status_code, 200)
        self.assertIn(fieras_instance, response.context['object_list'])
        self.assertNotIn(benito_instance, response.context['object_list'])

    def test_it_does_not_repeat_instances(self):
        '''It does not repeat instances'''
        fiera = User.objects.create_user(username='fiera',
            password="feroz",
            email="fiera@ciudadanointeligente.org")
        fieras_instance = WriteItInstance.objects.create(name='test_mode_instance',
            owner=fiera)
        fieras_instance.config.testing_mode = False
        fieras_instance.config.save()
        c = Client()
        c.login(username='fiera', password="feroz")
        response = c.get(reverse('instance_list'))
        self.assertEquals(response.context['object_list'].count(fieras_instance), 1)
