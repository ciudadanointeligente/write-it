from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Subscriber, Message, WriteItInstance, Confirmation, Answer, NewAnswerNotificationTemplate
from popit.models import Person
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User

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
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='public non confirmated message', 
            writeitinstance= self.moderation_not_needed_instance, 
            persons = [self.person1])
        Confirmation.objects.create(message=message)

        subscriber_amount = Subscriber.objects.filter(message=message).count()
        self.assertEquals(subscriber_amount, 0)
        message.recently_confirmated()

        subscription = Subscriber.objects.get(message=message)

        self.assertEquals(subscription.email, message.author_email)


    def test_create_a_message_without_author_email(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe',
            subject='public non confirmated message', 
            writeitinstance= self.moderation_not_needed_instance, 
            persons = [self.person1])
        Confirmation.objects.create(message=message)

        message.recently_confirmated()
        subscriber_amount = Subscriber.objects.filter(message=message).count()
        self.assertEquals(subscriber_amount, 0)



class NewAnswerToSubscribersMessageTemplate(TestCase):
    def setUp(self):
        self.new_answer_html = ''
        with open('nuntium/templates/nuntium/mails/new_answer.html', 'r') as f:
            self.new_answer_html += f.read()

        super(NewAnswerToSubscribersMessageTemplate, self).setUp()
        self.instance = WriteItInstance.objects.all()[0]
        self.instance.new_answer_notification_template.delete()
        self.message = Message.objects.all()[0]
        self.pedro = Person.objects.all()[0]
        self.owner = User.objects.all()[0]
        self.answer = Answer.objects.create(
            content="Ola ke ase? pedalea o ke ase?",
            person=self.pedro,
            message=self.message
            )
        template_str = get_template('nuntium/mails/new_answer.html')
        d = Context({ 
            'user': self.message.author_name,
            'person':self.pedro,
            'message':self.message,
            'answer':self.answer
             })
        self.template_str = template_str.render(d)


    def test_creation_of_one(self):
        
        notification_template = NewAnswerNotificationTemplate.objects.create(
            template = self.template_str,
            writeitinstance=self.instance
            )

        self.assertTrue(notification_template)
        self.assertEquals(notification_template.template, self.template_str)
        self.assertEquals(notification_template.writeitinstance, self.instance)
        self.assertEquals(self.instance.new_answer_notification_template, notification_template)


    def test_when_I_create_a_new_writeitinstance_then_a_notification_template_is_created(self):

        instance  = WriteItInstance.objects.create(name='instance 234', slug='instance-234', owner=self.owner)
        
        notification_template = instance.new_answer_notification_template
        self.assertTrue(notification_template)
        self.assertEquals(notification_template.template, self.new_answer_html)
