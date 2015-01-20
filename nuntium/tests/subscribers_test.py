from global_test_case import GlobalTestCase as TestCase
from ..models import Subscriber, Message, WriteItInstance, \
    Confirmation, Answer, NewAnswerNotificationTemplate
from popit.models import Person
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from django.core import mail
from django.conf import settings
from django.template.loader import get_template_from_string
import os
from django.test.utils import override_settings


subject_template = '%(person)s has answered to your message %(message)s'
script_dir = os.path.dirname(__file__)


class SubscribersTestCase(TestCase):
    def setUp(self):
        super(SubscribersTestCase, self).setUp()
        self.moderation_not_needed_instance = WriteItInstance.objects.all()[0]
        self.message = Message.objects.all()[0]
        self.person1 = Person.objects.all()[0]

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
        self.new_answer_html = ''
        with open(os.path.join(script_dir, '../templates/nuntium/mails/new_answer.html'), 'r') as f:
            self.new_answer_html += f.read()
        super(NewAnswerToSubscribersMessageTemplate, self).setUp()
        self.instance = WriteItInstance.objects.all()[0]

        self.message = Message.objects.all()[0]
        self.pedro = Person.objects.all()[0]
        self.owner = User.objects.all()[0]
        self.answer = Answer.objects.create(
            content="Ola ke ase? pedalea o ke ase?",
            person=self.pedro,
            message=self.message
            )
        template_str = get_template('nuntium/mails/new_answer.html')
        d = Context(
            {'user': self.message.author_name,
             'person': self.pedro,
             'message': self.message,
             'answer': self.answer,
             })
        self.template_str = template_str.render(d)
        self.instance.new_answer_notification_template.delete()

    def test_creation_of_one(self):
        # content_template = ''
        # with open('nuntium/mails/new_answer.html', 'r') as f:
        #     content_template += f.read()
        # print content_template
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
        new_answer_html = ''
        with open(os.path.join(script_dir, '../templates/nuntium/mails/new_answer.html'), 'r') as f:
            new_answer_html += f.read()

        new_answer_txt = ''
        with open(os.path.join(script_dir, '../templates/nuntium/mails/new_answer.txt'), 'r') as f:
            new_answer_txt += f.read()

        notification_template = NewAnswerNotificationTemplate.objects.create(writeitinstance=self.instance)

        self.assertEquals(notification_template.template_html, new_answer_html)
        self.assertEquals(notification_template.template_text, new_answer_txt)
        self.assertEquals(notification_template.subject_template, '%(person)s has answered to your message %(message)s')

    def test_when_I_create_a_new_writeitinstance_then_a_notification_template_is_created(self):
        instance = WriteItInstance.objects.create(name=u'instance 234', slug=u'instance-234', owner=self.owner)

        notification_template = instance.new_answer_notification_template
        self.assertTrue(notification_template)
        self.assertEquals(notification_template.template_html, self.new_answer_html)
        self.assertEquals(notification_template.subject_template, subject_template)


class NewAnswerNotificationToSubscribers(TestCase):
    def setUp(self):
        super(NewAnswerNotificationToSubscribers, self).setUp()
        self.instance = WriteItInstance.objects.all()[0]
        self.message = Message.objects.all()[0]
        self.subscriber = Subscriber.objects.create(message=self.message, email=self.message.author_email)
        self.pedro = Person.objects.all()[0]
        self.owner = User.objects.all()[0]
        self.instance.new_answer_notification_template.subject_template = 'weeena pelao %(person)s %(message)s'
        self.instance.new_answer_notification_template.save()
        self.template_str_html = get_template_from_string(self.instance.new_answer_notification_template.template_html)
        self.template_str_txt = get_template_from_string(self.instance.new_answer_notification_template.template_text)

    def create_a_new_answer(self):
        self.answer = Answer.objects.create(
            content="Ola ke ase? pedalea o ke ase?",
            person=self.pedro,
            message=self.message,
            )
        # template_str = get_template('nuntium/mails/new_answer.html')

    def test_when_an_answer_is_created_then_a_mail_is_sent_to_the_subscribers(self):
        self.create_a_new_answer()
        d = Context(
            {'user': self.message.author_name,
             'person': self.pedro,
             'message': self.message,
             'answer': self.answer,
             })

        # PLEASE TEST HTML
        # template_str_html = self.template_str_html.render(d)
        # I'M NOT TESTED PLEASE DO!!!
        template_str_txt = self.template_str_txt.render(d)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.subscriber.email)
        self.assertEquals(mail.outbox[0].body, template_str_txt)
        subject = self.instance.new_answer_notification_template.subject_template % {
            'person': self.pedro.name,
            'message': self.message.subject,
        }
        self.assertEquals(mail.outbox[0].subject, subject)

        self.assertEquals(
            mail.outbox[0].from_email,
            self.instance.slug + "@" + settings.DEFAULT_FROM_DOMAIN,
            )

    @override_settings(SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL=True)
    def test_send_subscribers_notice_from_a_single_unified_email(self):
        '''Send emails from default from email'''
        self.create_a_new_answer()
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_owner_of_the_instance_is_notified_when_a_new_answer_comes_in(self):
        self.instance.notify_owner_when_new_answer = True
        self.instance.save()
        self.create_a_new_answer()
        user = User.objects.get(email="admin@admines.cl")
        d = Context(
            {'user': user,
             'person': self.pedro,
             'message': self.message,
             'answer': self.answer,
             })

        # FIXME - PLEASE TEST HTML
        # template_str_html = self.template_str_html.render(d)
        # I'M NOT TESTED PLEASE DO!!!
        template_str_txt = self.template_str_txt.render(d)

        # now test the email to the owner
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(len(mail.outbox[1].to), 1)
        self.assertEquals(mail.outbox[1].to[0], user.email)
        self.assertEquals(mail.outbox[1].body, template_str_txt)
        subject = self.instance.new_answer_notification_template.subject_template % {
            'person': self.pedro,
            'message': self.message.subject,
        }
        self.assertEquals(mail.outbox[0].subject, subject)
        self.assertEquals(
            mail.outbox[0].from_email,
            self.instance.slug + "@" + settings.DEFAULT_FROM_DOMAIN,
            )
