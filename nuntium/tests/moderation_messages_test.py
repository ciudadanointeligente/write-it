# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from ..models import Message, WriteItInstance, \
    Moderation, Confirmation, OutboundMessage
from popolo.models import Person
from django.core import mail
from subdomains.utils import reverse
import datetime
from mock import patch
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.conf import settings
from django.test.utils import override_settings
from django.utils.unittest import skip


class ModerationMessagesTestCase(TestCase):
    def setUp(self):
        super(ModerationMessagesTestCase, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.private_message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Subject 1',
            public=False,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        self.confirmation = Confirmation.objects.create(message=self.private_message)
        self.owner = self.writeitinstance1.owner
        self.owner.set_password('feroz')
        self.owner.save()

    def test_private_messages_confirmation_created_move_from_new_to_needs_moderation(self):
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.recently_confirmated()

        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message)
        self.assertEquals(outbound_message_to_pedro.status, 'needmodera')

    def test_private_message_is_not_accesible(self):
        self.confirmation.confirmated_at = datetime.datetime.now()
        self.confirmation.save()
        self.private_message.confirmated = True
        self.private_message.save()
        url = self.private_message.get_absolute_url()
        response = self.client.get(url)

        self.assertEquals(response.status_code, 404)

    def test_cannot_view_unmoderated_message(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.config.save()

        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=True,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message.recently_confirmated()
        url = message.get_absolute_url()
        response = self.client.get(url)

        self.assertFalse(message.moderated)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['awaiting_moderation'], True)
        self.assertContains(response, 'This message is awaiting moderation')

    def test_can_view_moderated_message(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=True,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message.recently_confirmated()

        url = message.get_absolute_url()
        response = self.client.get(url)

        self.assertTrue(message.moderated)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['awaiting_moderation'], False)
        self.assertContains(response, 'Fiera es una perra feroz')

    def test_can_view_message_with_moderated_none(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=True,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message.recently_confirmated()

        message.moderated = None
        message.save()

        url = message.get_absolute_url()
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['awaiting_moderation'], False)
        self.assertContains(response, 'Fiera es una perra feroz')

    def test_outbound_messages_of_a_confirmed_message_are_waiting_for_moderation(self):
        # I need to do a get to the confirmation url
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        url = reverse(
            'confirm',
            subdomain=self.private_message.writeitinstance.slug,
            kwargs={
                'slug': self.confirmation.key
                },
            )
        self.client.get(url)
        # this works proven somewhere else
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message)
        self.assertEquals(outbound_message_to_pedro.status, 'needmodera')

    def test_create_a_moderation(self):
        #I make sure that uuid.uuid1 is called and I get a sort of random key
        with patch('uuid.uuid1') as string:
            string.return_value.hex = 'oliwi'
            message = Message.objects.create(
                content='Content 1',
                author_name='Felipe',
                author_email="falvarez@votainteligente.cl",
                subject='Fiera es una perra feroz',
                public=False,
                writeitinstance=self.writeitinstance1,
                persons=[self.person1],
                )

            self.assertFalse(message.moderation is None)
            self.assertEquals(message.moderation.key, 'oliwi')
            string.assert_called()

    # issue 114 found at https://github.com/ciudadanointeligente/write-it/issues/114

    # we don't send moderation emails anymore
    def test_only_send_a_confirmation_email(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.config.save()

        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=False,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertEquals(len(mail.outbox), 1)
        message.recently_confirmated()
        self.assertEquals(len(mail.outbox), 1)

    def test_message_has_a_method_for_moderate(self):
        self.confirmation.confirmated_at = datetime.datetime.now()
        self.confirmation.save()
        self.private_message.confirmated = True
        self.private_message.save()

        self.private_message.moderate()
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message)

        self.assertTrue(self.private_message.moderated)
        self.assertEquals(outbound_message_to_pedro.status, 'ready')

    def test_message_that_has_not_been_confirmed_cannot_be_moderated(self):
        # this message has not been confirmed
        # and is private therefore requires moderation
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=False,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        with self.assertRaises(ValidationError):
            # this was taken from here
            # http://stackoverflow.com/questions/8215653/using-a-context-manager-with-python-assertraises#8215739
            try:
                message.moderate()
            except ValidationError as e:
                self.assertEqual(e.message,
                    _('The message needs to be confirmated first',))
                raise

        self.assertFalse(message.moderated)
        outbound_message_to_pedro = OutboundMessage.objects.get(message=message)
        self.assertEquals(outbound_message_to_pedro.status, 'new')

    def test_error_if_moderate_public_message_created_when_moderation_off(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = False
        self.writeitinstance1.config.save()
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=True,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message.recently_confirmated()

        # Marking a message confirmed while moderation is off marks it
        # as moderated; moderate() should never be called on a message
        # that's marked as already moderated, but check that an
        # exception is raised in the rare situations where it might.
        with self.assertRaisesRegexp(
                ValidationError,
                'Cannot moderate an already moderated message'):
            message.moderate()

        outbound_message_to_pedro = OutboundMessage.objects.get(message=message)
        self.assertEquals(outbound_message_to_pedro.status, 'ready')

    # for https://github.com/ciudadanointeligente/write-it/issues/704
    def test_moderation_created_for_old_messages_after_moderation_turned_on(self):
        # we use a private message because they always require
        # moderation
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=False,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        message.recently_confirmated()

        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.config.save()

        message.moderate()

        self.assertTrue(message.moderated)
        outbound_message_to_pedro = OutboundMessage.objects.get(message=message)
        self.assertEquals(outbound_message_to_pedro.status, 'ready')

    def test_there_is_a_moderation_url_that_sets_the_message_to_ready(self):
        self.client.login(username=self.owner.username, password='feroz')
        self.confirmation.confirmated_at = datetime.datetime.now()
        self.confirmation.save()
        self.private_message.confirmated = True
        self.private_message.save()

        url = reverse('moderation_accept',
            subdomain=self.private_message.writeitinstance.slug,
            kwargs={
                'slug': self.private_message.moderation.key
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/moderation_accepted.html')

        #private_message = Message.objects.get(id=self.private_message.id)
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message.id)
        self.assertEquals(outbound_message_to_pedro.status, 'ready')
        private_message = Message.objects.get(id=self.private_message.id)
        self.assertTrue(private_message.moderated)

    def test_moderation_get_success_url(self):
        expected_url = reverse('moderation_accept',
            self.private_message.writeitinstance.slug,
            kwargs={
                'slug': self.private_message.moderation.key
            })
        self.assertEquals(self.private_message.moderation.get_success_url(), expected_url)

    def test_moderation_get_reject_url(self):
        expected_url = reverse('moderation_rejected',
            subdomain=self.private_message.writeitinstance.slug,
            kwargs={
                'slug': self.private_message.moderation.key
            })
        self.assertEquals(self.private_message.moderation.get_reject_url(), expected_url)

    def test_there_is_a_reject_moderation_url_that_hides_the_message(self):
        '''
        This is the case when you proud owner of a writeitInstance
        think that the private message should not go anywhere
        and it should be hidden
        '''
        self.client.login(username=self.owner.username, password='feroz')
        # Ok I'm going to make the message public
        public_message = self.private_message
        public_message.public = True
        public_message.save()

        url = reverse(
            'moderation_rejected',
            subdomain=public_message.writeitinstance.slug,
            kwargs={
                'slug': public_message.moderation.key
                })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/moderation_rejected.html')
        # If someone knows how to do the DoesNotExist or where to extend from
        # I could do a self.assertRaises but I'm not taking any more time in this
        message = Message.objects.get(id=public_message.id)
        self.assertFalse(message.public)
        self.assertTrue(message.moderated)

    def test_when_moderation_needed_a_mail_for_its_owner_is_sent(self):
        self.private_message.recently_confirmated()
        self.assertEquals(len(mail.outbox), 1)

    def test_creates_automatically_a_moderation_when_a_private_message_is_created(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            public=False,
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

        self.assertFalse(message.moderation is None)

    def test_a_moderation_does_not_change_its_key_on_save(self):
        '''
        I found that everytime I did resave a moderation
        it key was regenerated
        '''
        previous_key = self.private_message.moderation.key
        self.private_message.moderation.save()
        moderation = Moderation.objects.get(message=self.private_message)
        post_key = moderation.key

        self.assertEquals(previous_key, post_key)

    def test_moderates_method(self):
        moderation = Moderation.objects.get(message=self.private_message)
        moderation.success()

        message = Message.objects.get(moderation=moderation)
        self.assertTrue(message.moderated)

    # this test is for the issue https://github.com/ciudadanointeligente/write-it/issues/186
    @skip('Message creation is no longer in the instance detail view')
    def test_confirmated_but_not_moderated_message_in_a_moderable_instance_is_in_needs_moderation_status(self):
        self.writeitinstance1.config.moderation_needed_in_all_messages = True
        self.writeitinstance1.config.save()

        data = {
            'author_email': u'falvarez@votainteligente.cl',
            'author_name': u'feli',
            'public': True,
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'persons': [self.person1.id],
            }
        url = self.writeitinstance1.get_absolute_url()
        self.client.post(url, data, follow=True)
        message = Message.objects.get(
            author_name="feli",
            author_email="falvarez@votainteligente.cl",
            subject="Fiera no está",
            content='¿Dónde está Fiera Feroz? en la playa?')
        confirmation = Confirmation.objects.get(message=message)

        self.client.get(confirmation.get_absolute_url())

        # one message to Pedro
        outbound_message = OutboundMessage.objects.get(message=message)
        # Here I have the bug!!!!!
        self.assertEquals(outbound_message.status, 'needmodera')
        # This one is the bug!!\

    def test_non_authenticated_users_cant_accept_messages(self):
        """Moderation accept links require users to be logged in"""
        self.confirmation.confirmated_at = datetime.datetime.now()
        self.confirmation.save()
        self.private_message.confirmated = True
        self.private_message.save()

        url = reverse('moderation_accept',
            subdomain=self.private_message.writeitinstance.slug,
            kwargs={
                'slug': self.private_message.moderation.key
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message.id)
        self.assertEquals(outbound_message_to_pedro.status, 'new')
        private_message = Message.objects.get(id=self.private_message.id)
        self.assertFalse(private_message.moderated)

    def test_non_authenticated_users_cant_reject_messages(self):
        """Moderation reject links require users to be logged in"""
        self.confirmation.confirmated_at = datetime.datetime.now()
        self.confirmation.save()
        self.private_message.confirmated = True
        self.private_message.save()

        url = reverse('moderation_rejected',
            subdomain=self.private_message.writeitinstance.slug,
            kwargs={
                'slug': self.private_message.moderation.key
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message.id)
        self.assertEquals(outbound_message_to_pedro.status, 'new')
        private_message = Message.objects.get(id=self.private_message.id)
        self.assertFalse(private_message.moderated)
