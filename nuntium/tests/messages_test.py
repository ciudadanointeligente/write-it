from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord, Confirmation
from popit.models import Person, ApiInstance
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
import datetime


class TestMessages(TestCase):

    def setUp(self):
        super(TestMessages,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.person2 = Person.objects.all()[1]


    def test_create_message(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        self.assertTrue(message)
        self.assertEquals(message.content, "Content 1")
        self.assertEquals(message.subject, "Fiera es una perra feroz")
        self.assertEquals(message.writeitinstance, self.writeitinstance1)
        self.assertEquals(message.slug, slugify(message.subject))
        self.assertTrue(message.public)


    def test_update_a_message_does_not_need_persons(self):
        message1 = Message.objects.all()[0]

        previous_people = message1.people

        message1.slug = 'a-new-slug1'

        message1.save()

        self.assertEquals(message1.people, previous_people)


    def test_message_has_a_permalink(self):
        message1 = Message.objects.all()[0]
        expected_url = reverse('message_detail', kwargs={'slug':message1.slug})

        self.assertEquals(expected_url, message1.get_absolute_url())





    def test_two_messages_with_the_same_subject_but_different_slug(self):
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

        message2 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

        message3 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])


        self.assertEquals(message1.slug, slugify(message1.subject))
        self.assertEquals(message2.slug, slugify(message2.subject)+"-2")
        self.assertEquals(message3.slug, slugify(message3.subject)+"-3")


    def test_a_person_with_two_contacts_method_people(self):
        contact = Contact.objects.create(person=self.person1
            , value=u"another@contact.cl"
            , contact_type=self.person1.contact_set.all()[0].contact_type)
        
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])


        self.assertEquals(message.people, [self.person1])


    def test_resave_a_message_should_not_change_slug(self):
        #There are a lot of good solutions for this problem but this
        #is the easyest one
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        previous_slug = message1.slug
        #message1 now has a slug
        message1.subject = 'Some other subject and stuff'
        message1.save()

        self.assertEquals(message1.slug, previous_slug)


    def test_a_message_has_a_people_property(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1, self.person2])

        self.assertEquals(message.people, [self.person1, self.person2])


    def test_message_unicode(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])

        self.assertEquals(message.__unicode__(), _('%(subject)s at %(instance)s') % {
            'subject':message.subject,
            'instance':self.writeitinstance1.name
            })

    def test_outboundmessage_create_without_manager(self):
        message = Message(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        
        self.assertEquals(message.outboundmessage_set.count(), 1)


    def test_it_creates_outbound_messages_only_once(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        self.assertEquals(OutboundMessage.objects.filter(message=message).count(), 1)

    def test_it_raises_typeerror_when_no_contacts_are_present(self):
        with self.assertRaises(TypeError):
            Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1)


class MessageDetailView(TestCase):
    def setUp(self):
        super(MessageDetailView,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        Confirmation.objects.create(message=self.message, confirmated_at = datetime.datetime.now())


    def test_get_message_detail_page(self):
        #I'm kind of feeling like I need 
        #something like rspec or cucumber
        
        url = reverse('message_detail', kwargs={'slug':self.message.slug})
        self.assertTrue(url)

        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], self.message)



    




