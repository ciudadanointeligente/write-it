from global_test_case import GlobalTestCase as TestCase
from instance.models import WriteItInstance
from ..models import Confirmation, OutboundMessage
from ..models import Message
from popolo.models import Person
from contactos.models import Contact
from datetime import datetime
from django.core import mail
from plugin_mock.mental_message_plugin import MentalMessage
from subdomains.utils import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.test.utils import override_settings
from mock import patch


class ConfirmationTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTestCase, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.Marcel = Person.objects.get(id=2)
        felipe = Person.objects.get(id=3)
        self.channel = MentalMessage()
        self.user = User.objects.get(id=1)
        self.mental_contact1 = Contact.objects.create(
            person=felipe,
            contact_type=self.channel.get_contact_type(),
            writeitinstance=self.writeitinstance1)

        self.message = Message.objects.create(
            content='hello there',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Wow!',
            writeitinstance=self.writeitinstance1,
            persons=[felipe],
            )
        self.message2 = Message.objects.create(
            content='hello there',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Wow!',
            writeitinstance=self.writeitinstance1,
            persons=[self.Marcel],
            )

    def test_instanciate(self):
        confirmation = Confirmation(message=self.message)
        self.assertTrue(confirmation)
        self.assertEquals(len(confirmation.key.strip()), 0)

    def test_creation_and_save(self):
        confirmation = Confirmation.objects.create(message=self.message)

        self.assertTrue(confirmation.id)
        self.assertEquals(confirmation.message, self.message)
        self.assertEquals(len(confirmation.key.strip()), 32)
        self.assertTrue(isinstance(confirmation.created, datetime))
        self.assertTrue(confirmation.confirmated_at is None)

    def test_confirmation_has_a_key_generator(self):
        key1 = Confirmation.key_generator()
        key2 = Confirmation.key_generator()

        self.assertNotEquals(key1, key2)

    def test_duplication(self):
        # Serioulsly I'm getting to many times Duplicate entry for key 'key'
        confirmation1 = Confirmation.objects.create(message=self.message)
        confirmation2 = Confirmation.objects.create(message=self.message2)

        self.assertNotEquals(confirmation1.key, confirmation2.key)

    def test_it_sends_an_email_to_the_author_asking_for_confirmation(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse(
            'confirm',
            subdomain=self.message.writeitinstance.slug,
            kwargs={'slug': confirmation.key},
            )
        confirmation_full_url = url

        self.assertEquals(len(mail.outbox), 1)  # it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, u'Please confirm your message to Felipe')
        self.assertTrue(self.message.author_name in mail.outbox[0].body)
        self.assertIn(confirmation_full_url, mail.outbox[0].body)
        self.assertTrue(url in mail.outbox[0].body)

        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(self.message.author_email in mail.outbox[0].to)
        expected_from_email = self.message.writeitinstance.slug + "@" + settings.DEFAULT_FROM_DOMAIN
        self.assertEquals(mail.outbox[0].from_email, expected_from_email)

    def test_sends_confirmation_from_a_custom_domain_if_specified(self):
        '''Sending confirmation from a custom domain if specified'''
        config = self.message.writeitinstance.config
        config.custom_from_domain = "custom.domain.cl"
        config.email_host = 'cuttlefish.au.org'
        config.email_host_password = 'f13r4'
        config.email_host_user = 'fiera'
        config.email_port = 25
        config.email_use_tls = True
        config.save()
        Confirmation.objects.create(message=self.message)
        self.assertEquals(len(mail.outbox), 1)
        expected_from_email = self.message.writeitinstance.slug + "@" + config.custom_from_domain
        confirmation_mail = mail.outbox[0]
        self.assertEquals(confirmation_mail.from_email, expected_from_email)
        connection = confirmation_mail.connection
        self.assertEquals(connection.host, config.email_host)
        self.assertEquals(connection.password, config.email_host_password)
        self.assertEquals(connection.username, config.email_host_user)
        self.assertEquals(connection.port, config.email_port)
        self.assertEquals(connection.use_tls, config.email_use_tls)
        '''
        I'm moving all the site to use cuttlefish but in the meantime
        in order to test I'm using this specific config per instance

        EMAIL_HOST = 'cuttlefish.oaf.org.au'
        EMAIL_PORT = 2525
        EMAIL_HOST_USER = 'writeit'
        EMAIL_HOST_PASSWORD = 'FieraFerozEsElMejorPerroDelMundo'
        EMAIL_USE_TLS = True
        '''

    @override_settings(SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL=True)
    def test_send_confirmation_from_a_single_email_address(self):
        '''
        In some cases it is needed that the email is sent from a single
        email, that email should be the default_from_email
        '''
        Confirmation.objects.create(message=self.message)
        expected_from_email = settings.DEFAULT_FROM_EMAIL
        self.assertEquals(mail.outbox[0].from_email, expected_from_email)

    def test_confirmation_get_absolute_url(self):
        confirmation = Confirmation.objects.create(message=self.message)
        expected_url = reverse(
            'confirm',
            subdomain=self.message.writeitinstance.slug,
            kwargs={'slug': confirmation.key},
            )
        self.assertEquals(expected_url, confirmation.get_absolute_url())

    def test_access_the_confirmation_url(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse(
            'confirm',
            subdomain=self.message.writeitinstance.slug,
            kwargs={'slug': confirmation.key},
            )
        message_url = reverse('thread_read',
            subdomain=self.message.writeitinstance.slug,
            kwargs={'slug': self.message.slug}
            )
        response = self.client.get(url)
        self.assertRedirects(response, message_url)

        confirmation = Confirmation.objects.get(id=confirmation.id)
        self.assertTrue(confirmation.confirmated_at is not None)
        outbound_messages = OutboundMessage.objects.filter(message=confirmation.message)

        self.assertEquals(outbound_messages[0].status, "ready")

    def test_confirmed_property(self):
        confirmation = Confirmation.objects.create(message=self.message)

        self.assertFalse(confirmation.is_confirmed)

        confirmation.confirmated_at = datetime.now()
        confirmation.save()

        self.assertTrue(confirmation.is_confirmed)

    def test_it_does_not_confirm_twice(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse(
            'confirm',
            subdomain=self.message.writeitinstance.slug,
            kwargs={'slug': confirmation.key},
            )
        response1 = self.client.get(url)
        message_thread = reverse(
            'thread_read', subdomain=self.message.writeitinstance.slug,
            kwargs={
                'slug': self.message.slug
            })
        response2 = self.client.get(url)

        self.assertEquals(response1.status_code, 302)
        self.assertRedirects(response2, message_thread)

    def test_i_cannot_access_a_non_confirmed_message(self):
        Confirmation.objects.create(message=self.message)
        url = reverse('thread_read', subdomain=self.message.writeitinstance.slug, kwargs={'slug': self.message.slug})
        response = self.client.get(url)

        self.assertEquals(response.status_code, 404)


class EmailSendingErrorHandling(TestCase):
    def setUp(self):
        super(EmailSendingErrorHandling, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.Marcel = Person.objects.get(id=2)
        felipe = Person.objects.get(id=3)
        self.channel = MentalMessage()
        self.user = User.objects.get(id=1)
        self.mental_contact1 = Contact.objects.create(person=felipe,
            contact_type=self.channel.get_contact_type(),
            writeitinstance=self.writeitinstance1)
        self.message = Message.objects.create(
            content='hello there',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Wow!',
            writeitinstance=self.writeitinstance1,
            persons=[felipe],
            )
        self.message2 = Message.objects.create(
            content='hello there',
            author_name='Marcel',
            author_email="maugsburger@votainteligente.cl",
            subject='Wow!',
            writeitinstance=self.writeitinstance1,
            persons=[self.Marcel],
            )

    def test_confirmation_sending_error_does_not_destroy_message(self):
        with patch("django.core.mail.EmailMultiAlternatives.send") as send:
            send.side_effect = Exception("The message was not sent")
            with self.assertRaisesRegexp(Exception, r'The message was not sent'):
                Confirmation.objects.create(message=self.message2)
            self.assertEquals(len(mail.outbox), 0)

        messages = Message.objects.filter(id=self.message2.id)
        self.assertEquals(messages.count(), 1)
        self.assertTrue(messages[0].confirmation)
