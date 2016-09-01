from global_test_case import GlobalTestCase as TestCase
from instance.models import PopoloPerson, WriteItInstance
from ..models import Subscriber, Message, \
    Confirmation, Answer, NewAnswerNotificationTemplate
from django.contrib.auth.models import User
from django.core import mail
from django.conf import settings
import os
from django.test.utils import override_settings

subject_template = u'{person} has replied to your message {subject}\n'
script_dir = os.path.dirname(__file__)


class SubscribersTestCase(TestCase):
    def setUp(self):
        super(SubscribersTestCase, self).setUp()
        self.moderation_not_needed_instance = WriteItInstance.objects.get(id=1)
        self.message = Message.objects.get(id=1)
        self.person1 = PopoloPerson.objects.get(id=1)

    def test_create_a_new_subscriber(self):
        subscriber = Subscriber.objects.create(message=self.message, email='felipe@lab.ciudadanointeligente.org')

        self.assertTrue(subscriber)
        self.assertEquals(subscriber.message, self.message)
        self.assertEquals(subscriber.email, 'felipe@lab.ciudadanointeligente.org')
        self.assertIn(subscriber, self.message.subscribers.all())

    def test_when_a_new_message_is_confirmated_then_a_subscriber_is_created(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='public non confirmated message',
            writeitinstance=self.moderation_not_needed_instance,
            persons=[self.person1],
            )
        Confirmation.objects.create(message=message)

        subscriber_amount = Subscriber.objects.filter(message=message).count()
        self.assertEquals(subscriber_amount, 0)
        message.recently_confirmated()

        subscription = Subscriber.objects.get(message=message)

        self.assertEquals(subscription.email, message.author_email)

    def test_create_a_message_without_author_email(self):
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            subject='public non confirmated message',
            writeitinstance=self.moderation_not_needed_instance,
            persons=[self.person1],
            )
        Confirmation.objects.create(message=message)

        message.recently_confirmated()
        subscriber_amount = Subscriber.objects.filter(message=message).count()
        self.assertEquals(subscriber_amount, 0)


class NewAnswerToSubscribersMessageTemplate(TestCase):
    def setUp(self):
        super(NewAnswerToSubscribersMessageTemplate, self).setUp()
        self.instance = WriteItInstance.objects.get(id=1)

        self.message = Message.objects.get(id=1)
        self.pedro = PopoloPerson.objects.get(id=1)
        self.owner = User.objects.get(id=1)
        self.answer = Answer.objects.create(
            content="Ola ke ase? pedalea o ke ase?",
            person=self.pedro,
            message=self.message
            )
        self.instance.new_answer_notification_template.delete()

    def test_creation_of_one(self):
        notification_template = NewAnswerNotificationTemplate.objects.create(
            template_html=u"asdasd",
            template_text=u"asdasd",
            writeitinstance=self.instance,
            subject_template=subject_template,
            )

        self.assertTrue(notification_template)
        self.assertEquals(notification_template.template_html, "asdasd")
        self.assertEquals(notification_template.template_text, "asdasd")
        self.assertEquals(notification_template.writeitinstance, self.instance)
        self.assertEquals(self.instance.new_answer_notification_template, notification_template)

    def test_notification_template_unicode(self):
        notification_template = NewAnswerNotificationTemplate.objects.create(
            template_html=u"asdasd",
            template_text=u"asdasd",
            writeitinstance=self.instance,
            subject_template=subject_template,
            )

        self.assertEquals(notification_template.__unicode__(), "Notification template for %s" % (self.instance.name))

    def test_a_new_one_is_always_created_with_some_default_values(self):
        new_answer_txt = u''
        subject_template = u''
        notification_template = NewAnswerNotificationTemplate.objects.create(writeitinstance=self.instance)

        self.assertEquals(notification_template.template_text, new_answer_txt)
        self.assertEquals(notification_template.subject_template, subject_template)

    def test_when_I_create_a_new_writeitinstance_then_a_notification_template_is_created(self):
        instance = WriteItInstance.objects.create(name=u'instance 234', slug=u'instance-234', owner=self.owner)

        notification_template = instance.new_answer_notification_template
        self.assertTrue(notification_template)
        self.assertEquals(notification_template.template_html, u'')
        self.assertEquals(notification_template.subject_template, u'')


class NewAnswerNotificationToSubscribers(TestCase):
    answer_content = "Ola ke ase? pedalea o ke ase?"

    def setUp(self):
        super(NewAnswerNotificationToSubscribers, self).setUp()
        self.instance = WriteItInstance.objects.get(id=1)
        self.message = Message.objects.get(id=1)
        self.subscriber = Subscriber.objects.create(message=self.message, email=self.message.author_email)
        self.pedro = PopoloPerson.objects.get(id=1)
        self.owner = User.objects.get(id=1)
        self.instance.new_answer_notification_template.subject_template = 'weeena pelao %(person)s %(message)s'
        self.instance.new_answer_notification_template.save()
        self.template_str_txt = self.instance.new_answer_notification_template.template_text

    def create_a_new_answer(self):
        self.answer = Answer.objects.create(
            content=self.answer_content,
            person=self.pedro,
            message=self.message,
            )

    def test_when_an_answer_is_created_then_a_mail_is_sent_to_the_subscribers(self):
        self.create_a_new_answer()

        context = {
            'author_name': 'Fiera',
            'person': 'Pedro',
            'subject': 'Subject 1',
            # Wer'e not including content here until we can include attachments too
            # See #930.
            # 'content': self.answer_content,
            'site_name': 'instance 1',
            'message_url_part': 'thread/subject-1',
            }

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertFalse(mail.outbox[0].alternatives)
        self.assertEquals(mail.outbox[0].to[0], self.subscriber.email)

        for key, value in context.items():
            self.assertIn(value, mail.outbox[0].body)

        subject = self.instance.new_answer_notification_template.subject_template.format(**context)

        self.assertEquals(mail.outbox[0].subject, subject)

        self.assertEquals(
            mail.outbox[0].from_email,
            self.instance.slug + "@" + settings.DEFAULT_FROM_DOMAIN,
            )

    def test_answer_notification_with_html(self):
        # Put some html in the new answer notification template
        new_answer_notification_template = self.message.writeitinstance.new_answer_notification_template
        new_answer_notification_template.template_html = '<b>{subject}</b>'

        self.create_a_new_answer()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(
            mail.outbox[0].alternatives,
            [(u'<b>Subject 1</b>', 'text/html')]
            )

    @override_settings(SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL=True)
    def test_send_subscribers_notice_from_a_single_unified_email(self):
        '''Send emails from default from email'''
        self.create_a_new_answer()
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_owner_of_the_instance_is_notified_when_a_new_answer_comes_in(self):
        self.instance.config.notify_owner_when_new_answer = True
        self.instance.config.save()
        self.create_a_new_answer()
        user = User.objects.get(email="admin@admines.cl")

        # now test the email to the owner
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(len(mail.outbox[1].to), 1)
        self.assertEquals(mail.outbox[1].to[0], user.email)

    def test_notify_the_owner_using_custom_domain(self):
        '''Using custom domain to notify the owner of an instance if custom config is provided'''
        config = self.instance.config
        config.custom_from_domain = "custom.domain.cl"
        config.email_host = 'cuttlefish.au.org'
        config.email_host_password = 'f13r4'
        config.email_host_user = 'fiera'
        config.email_port = 25
        config.email_use_tls = True
        config.save()
        self.instance.config.notify_owner_when_new_answer = True
        self.instance.config.save()
        self.create_a_new_answer()

        sent_mail = mail.outbox[1]
        self.assertEquals(
            sent_mail.from_email,
            self.instance.slug + "@" + config.custom_from_domain,
            )
        connection = sent_mail.connection
        self.assertEquals(connection.host, config.email_host)
        self.assertEquals(connection.password, config.email_host_password)
        self.assertEquals(connection.username, config.email_host_user)
        self.assertEquals(connection.port, config.email_port)
        self.assertEquals(connection.use_tls, config.email_use_tls)

        #I didn't have to change anything =/

    def test_send_subscriber_mail_from_custom_domain(self):
        '''The mail to the subscriber if new answer exists from a custom domain'''
        config = self.instance.config
        config.custom_from_domain = "custom.domain.cl"
        config.email_host = 'cuttlefish.au.org'
        config.email_host_password = 'f13r4'
        config.email_host_user = 'fiera'
        config.email_port = 25
        config.email_use_tls = True
        config.save()

        self.create_a_new_answer()
        sent_mail = mail.outbox[0]
        self.assertEquals(
            sent_mail.from_email,
            self.instance.slug + "@" + config.custom_from_domain,
            )
        connection = sent_mail.connection
        self.assertEquals(connection.host, config.email_host)
        self.assertEquals(connection.password, config.email_host_password)
        self.assertEquals(connection.username, config.email_host_user)
        self.assertEquals(connection.port, config.email_port)
        self.assertEquals(connection.use_tls, config.email_use_tls)
