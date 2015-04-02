from nuntium.user_section.tests.user_section_views_tests import UserSectionTestCase
from subdomains.utils import reverse
from nuntium.models import Message
import json
from django.contrib.auth.models import User


class HideAMessageTestCase(UserSectionTestCase):
    def setUp(self):
        super(HideAMessageTestCase, self).setUp()
        self.message = Message.objects.get(id=2)
        self.owner = self.message.writeitinstance.owner
        self.owner.set_password('feroz')
        self.owner.save()

    def test_post_to_the_url_for_toggle_public(self):
        '''There is a url for toggling public/hidden a message'''

        self.message.public = True
        self.message.save()

        url = reverse('toggle_public', subdomain=self.message.writeitinstance.slug, kwargs={
            'pk': self.message.pk})
        messages_url = reverse('messages_per_writeitinstance', subdomain=self.message.writeitinstance.slug)

        self.client.login(username=self.owner.username, password='feroz')

        # Set to private
        response = self.client.post(url)
        self.assertRedirects(response, messages_url)
        message = Message.objects.get(pk=self.message.pk)
        self.assertFalse(message.public)

        # Set to public again
        response = self.client.post(url)
        self.assertRedirects(response, messages_url)
        message = Message.objects.get(pk=self.message.pk)
        self.assertTrue(message.public)

    def test_non_logged_and_non_owner_toggling_public(self):
        '''
        Someone that is not logged in should not be able to toggle public
        '''
        self.message.public = True
        self.message.save()

        url = reverse('toggle_public', subdomain=self.message.writeitinstance.slug, kwargs={
            'pk': self.message.pk})

        self.client.post(url)
        self.assertTrue(Message.objects.get(id=self.message.id).public)

        other_user = User.objects.create_user(username="other", password='password')
        self.client.login(username=other_user.username, password='password')
        self.client.post(url)
        self.assertTrue(Message.objects.get(id=self.message.id).public)
