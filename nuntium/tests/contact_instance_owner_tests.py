from mock import patch

from subdomains.utils import reverse

from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from instance.views import send_email_to_instance_owner

@patch('instance.views.send_email_to_instance_owner')
class ContactFormTests(TestCase):

    def setUp(self):
        self.writeitinstance = WriteItInstance.objects.get(pk=1)

    def test_form_appears(self, fake_send):
        url = reverse(
            'contact_instance_owner',
            subdomain=self.writeitinstance.slug)
        self.assertEqual(
            url,
            'http://instance1.127.0.0.1.xip.io:8000/en/contact/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(
            response.content,
            r'<form method="post" action="[^"]+/contact/"')
        self.assertIn(
            '<input id="id_from_email" name="from_email" type="email"',
            response.content)
        self.assertRegexpMatches(
            response.content,
            '<textarea cols="\d+" id="id_message_content" name="message_content" rows="\d+">')
        self.assertFalse(fake_send.called)

    def test_post_malformed_email(self, fake_send):
        url = reverse(
            'contact_instance_owner',
            subdomain=self.writeitinstance.slug)
        response = self.client.post(
            url,
            {
                'from_email': 'foo',
                'message_content': "This is a sensible message",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {'from_email': [u'Enter a valid email address.']})
        self.assertIn('Enter a valid email address', response.content)
        self.assertFalse(fake_send.called)

    def test_post_both_empty(self, fake_send):
        url = reverse(
            'contact_instance_owner',
            subdomain=self.writeitinstance.slug)
        response = self.client.post(
            url,
            {
                'from_email': '',
                'message_content': '',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'message_content': [u'This field is required.'],
                'from_email': [u'This field is required.']
            }
        )
        self.assertIn('This field is required', response.content)
        self.assertFalse(fake_send.called)

    def test_message_required(self, fake_send):
        url = reverse(
            'contact_instance_owner',
            subdomain=self.writeitinstance.slug)
        response = self.client.post(
            url,
            {
                'from_email': 'foo@example.org',
                'message_content': '',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'message_content': [u'This field is required.'],
            }
        )
        self.assertIn('This field is required', response.content)
        self.assertFalse(fake_send.called)

    def test_message_send_is_called(self, fake_send):

        url = reverse(
            'contact_instance_owner',
            subdomain=self.writeitinstance.slug)
        response = self.client.post(
            url,
            {
                'from_email': 'foo@example.org',
                'message_content': 'This is a sensible message',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'http://instance1.127.0.0.1.xip.io:8000/en/'
        )
        self.assertTrue(fake_send.called)
        fake_send.assert_called_with(
            'Suggestion for missing email addresses',
            self.writeitinstance,
            'foo@example.org',
            'This is a sensible message')


@patch('instance.views.send_mail')
class SendEmailToOwnerTests(TestCase):

    def setUp(self):
        self.writeitinstance = WriteItInstance.objects.get(pk=1)

    def test_send_email(self, fake_send_mail):
        send_email_to_instance_owner(
            'Random subject',
            self.writeitinstance,
            'bar@mail.example.org',
            'This is another message.\nI remain, sir, etc.'
        )
        fake_send_mail.assert_called_with(
            'Suggestion for missing email addresses',
            'This is another message.\nI remain, sir, etc.',
            'bar@mail.example.org',
            [u'admin@admines.cl'])
