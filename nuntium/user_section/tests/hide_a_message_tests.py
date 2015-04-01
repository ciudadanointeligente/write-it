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

        self.client.login(username=self.owner.username, password='feroz')
        response = self.client.post(url)
        self.assertTrue(response.status_code, 200)
        the_message_again = Message.objects.get(id=self.message.id)
        self.assertFalse(the_message_again.public)
        # Because I'm hoping that this url is an ajax call I should receive
        # something that tells the UI that the message has turned into private now
        response_object = json.loads(response.content)
        # I think it should probably return the id of the
        # recently changed and the public status
        self.assertEquals(response_object['pk'], self.message.id)
        self.assertFalse(response_object['public'])
        # toggling Hidden
        response_public = json.loads(self.client.post(url).content)
        self.assertTrue(response_public['public'])

    def test_non_logged_and_non_owner_toggling_public(self):
        '''
        Someone that is not logged in should not be able to toggle public
        '''
        self.message.public = True
        self.message.save()

        url = reverse('toggle_public', subdomain=self.message.writeitinstance.slug, kwargs={
            'pk': self.message.pk})

        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)
        self.assertTrue(Message.objects.get(id=self.message.id).public)

        other_user = User.objects.create_user(username="other", password='password')
        self.client.login(username=other_user.username, password='password')
        response = self.client.post(url)
        self.assertTrue(Message.objects.get(id=self.message.id).public)
        self.assertEquals(response.status_code, 404)
