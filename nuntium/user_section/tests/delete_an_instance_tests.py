from subdomains.utils import reverse
from ...models import WriteItInstance
from django.test.client import Client
from .user_section_views_tests import UserSectionTestCase


class DeleteAnInstanceTestCase(UserSectionTestCase):
    def setUp(self):
        super(DeleteAnInstanceTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.writeitinstance.owner = self.user
        self.writeitinstance.save()

    def test_delete_url(self):
        '''There is a url to delete a writeitinstance'''
        url = reverse('delete_an_instance', kwargs={'slug': self.writeitinstance.slug})
        self.assertTrue(url)

    def test_get_to_url(self):
        '''Get the delete a WriteItInstance url returns a check if deleting'''
        url = reverse('delete_an_instance', kwargs={'slug': self.writeitinstance.slug})
        c = Client()
        c.login(username="fiera", password="feroz")
        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/profiles/writeitinstance_check_delete.html')
        # It's not yet deleted
        self.assertTrue(WriteItInstance.objects.get(id=self.writeitinstance.id))

    def test_post_to_url(self):
        '''When I post to the URL then it deletes the writeitinstance'''
        url = reverse('delete_an_instance', kwargs={'slug': self.writeitinstance.slug})
        c = Client()
        c.login(username="fiera", password="feroz")
        response = c.post(url)
        # Now it should be deleted
        self.assertFalse(WriteItInstance.objects.filter(id=self.writeitinstance.id))

        your_instances_url = reverse('your-instances')
        self.assertRedirects(response, your_instances_url)

    def test_get_if_not_logged_in(self):
        '''If I'm not logged in I cannot get the writeit instance delete url'''
        url = reverse('delete_an_instance', kwargs={'slug': self.writeitinstance.slug})
        c = Client()
        # this line is intentionally commented so I can show that I'm not logged in
        # c.login(username="fiera", password="feroz")
        # this line is intentionally commented so I can show that I'm not logged in
        response = c.get(url)
        self.assertEquals(response.status_code, 404)

    def test_post_if_not_logged_in(self):
        '''If I'm not logged in I cannot post to the writeit instance delete url'''
        url = reverse('delete_an_instance', kwargs={'slug': self.writeitinstance.slug})
        c = Client()
        # this line is intentionally commented so I can show that I'm not logged in
        # c.login(username="fiera", password="feroz")
        # this line is intentionally commented so I can show that I'm not logged in
        response = c.post(url)
        self.assertEquals(response.status_code, 404)
