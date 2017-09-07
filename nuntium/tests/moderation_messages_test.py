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

    def test_message_send_moderation_message(self):
        # Let's have some longer message content so we can keep an eye on the text wrapping.
        self.private_message.content = u'''A gaf fi dynnu sylw'r Prif Weinidog at y sefyllfa yn Ysbyty Penrhos Stanley yng Nghaergybi, lle mae un o'r ddwy ward wedi bod ar gau ers dros bythefnos erbyn hyn, oherwydd absenoldeb staff a diffyg staff wrth gefn, ac ni fydd y ward yn agor am bythefnos arall, tan 13 Ebrill—bron i dair wythnos a dweud y gwir?
A gaf i dynnu sylw'r Prif Weinidog hefyd at y sefyllfa yn Ysbyty Gwynedd yn ddiweddar, lle cadwyd etholwr i mi mewn ystafell storio dros nos wrth wella ar ôl llawdriniaeth, â’i declyn drip yn hongian oddi ar beg ar y wal, ac y rhoddwyd cloch bres Fictoraidd iddo i dynnu sylw’r nyrs. Mae'r nyrs yn gwneud gwaith gwych dan amgylchiadau anodd. A yw hynny'n swnio i'r Prif Weinidog fel GIG sydd ag adnoddau da ac yn cael ei reoli'n dda? Er bod gwleidyddiaeth cyni cyllidol yn gyfrifol am lawer o'r diffyg adnoddau, nid yw'n esgusodi camreolaeth y GIG gan Lywodraeth Cymru.'''
        self.private_message.save()

        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.send_moderation_mail()

        self.assertEquals(len(mail.outbox), 2)
        moderation_mail = mail.outbox[1]
        self.assertModerationMailSent(self.private_message, moderation_mail)
        expected_from_email = self.private_message.writeitinstance.slug + "@" + settings.DEFAULT_FROM_DOMAIN
        self.assertEquals(moderation_mail.from_email, expected_from_email)

    def test_send_moderation_message_from_custom_connection(self):
        '''If given a custom smtp config for its instance then
        it sends the moderation mail with this custom config '''
        config = self.private_message.writeitinstance.config
        config.custom_from_domain = "custom.domain.cl"
        config.email_host = 'cuttlefish.au.org'
        config.email_host_password = 'f13r4'
        config.email_host_user = 'fiera'
        config.email_port = 25
        config.email_use_tls = True
        config.save()

        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.send_moderation_mail()
        self.assertEquals(len(mail.outbox), 2)
        moderation_mail = mail.outbox[1]

        self.assertModerationMailSent(self.private_message, moderation_mail)
        expected_from_email = self.private_message.writeitinstance.slug + "@" + config.custom_from_domain

        self.assertEquals(moderation_mail.from_email, expected_from_email)
        connection = moderation_mail.connection
        self.assertEquals(connection.host, config.email_host)
        self.assertEquals(connection.password, config.email_host_password)
        self.assertEquals(connection.username, config.email_host_user)
        self.assertEquals(connection.port, config.email_port)
        self.assertEquals(connection.use_tls, config.email_use_tls)

    def test_not_using_any_custom_config(self):
        '''If not using any custom config the moderation
        mail does not use that connection'''
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.send_moderation_mail()

        self.assertEquals(len(mail.outbox), 2)
        moderation_mail = mail.outbox[1]
        connection = moderation_mail.connection
        self.assertFalse(hasattr(connection, 'host'))
        self.assertFalse(hasattr(connection, 'password'))
        self.assertFalse(hasattr(connection, 'username'))
        self.assertFalse(hasattr(connection, 'port'))
        self.assertFalse(hasattr(connection, 'use_tls'))

    @override_settings(SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL=True)
    def test_moderation_sent_from_default_from_email(self):
        '''Moderation is sent from default from email if specified'''
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.send_moderation_mail()
        moderation_mail = mail.outbox[1]
        expected_from_email = settings.DEFAULT_FROM_EMAIL
        self.assertEquals(moderation_mail.from_email, expected_from_email)

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

    def test_send_mails_only_once(self):
        with patch('nuntium.models.Message.send_moderation_mail') as send_moderation_mail:
            self.writeitinstance1.config.moderation_needed_in_all_messages = True
            self.writeitinstance1.config.save()

            send_moderation_mail.return_value = None
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

            # number_of_moderations = Moderation.objects.filter(message=message).count()
            send_moderation_mail.assert_called_once_with()

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
        # There should be two
        # One is created for confirmation
        # The other one is created for the moderation thing
        self.assertEquals(len(mail.outbox), 2)
        moderation_mail = mail.outbox[1]
        # it is sent to the owner of the instance
        self.assertEquals(moderation_mail.to[0], self.private_message.writeitinstance.owner.email)
        self.assertTrue(self.private_message.content in moderation_mail.body)
        self.assertTrue(self.private_message.subject in moderation_mail.body)
        self.assertTrue(self.private_message.author_name in moderation_mail.body)
        self.assertTrue(self.private_message.author_email in moderation_mail.body)
        url_rejected = (reverse('moderation_rejected',
                                subdomain=self.private_message.writeitinstance.slug,
                                kwargs={'slug': self.private_message.moderation.key})
                        )
        url_accept = (reverse('moderation_accept',
                              subdomain=self.private_message.writeitinstance.slug,
                              kwargs={'slug': self.private_message.moderation.key})
                      )

        self.assertIn(url_rejected, moderation_mail.body)
        self.assertIn(url_accept, moderation_mail.body)

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
