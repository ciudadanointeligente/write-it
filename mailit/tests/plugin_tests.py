from django.test import TestCase
from django.utils.unittest import skip
from mailit import MailChannel
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from nuntium.plugins import OutputPlugin
from mailit.models import MailItTemplate
from django.core import mail

class MailChannelTestCase(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 2')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact2 = Contact.objects.create(person=self.person2, contact_type=self.contact_type1, value= 'test@test.com')
        self.writeitinstance1 = WriteItInstance.objects.create(name='instance 1', api_instance= self.api_instance1)
        self.message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])

    def test_instaciate_mail_channel(self):
        channel = MailChannel()

        self.assertTrue(channel)
        self.assertTrue(isinstance(channel, OutputPlugin))

    def test_it_has_a_send_method(self):
        channel = MailChannel()

        self.assertTrue(channel.send)

    def test_it_has_a_contact_type(self):
        channel = MailChannel()

        self.assertTrue(channel.contact_type)
        self.assertEquals(channel.contact_type.label_name, "Electronic Mail")
        self.assertEquals(channel.contact_type.name, "e-mail")




class MailTemplateTestCase(TestCase):
    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 2')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact2 = Contact.objects.create(person=self.person2, contact_type=self.contact_type1, value= 'test@test.com')
        self.writeitinstance1 = WriteItInstance.objects.create(name='instance 1', api_instance= self.api_instance1)
        self.message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])

    def test_it_has_a_template(self):
        template = MailItTemplate.objects.create(writeitinstance=self.writeitinstance1,subject_template=u"hello somebody %(thing)s",content_template=u"content thing %(another)s asdas")

        self.assertTrue(template)
        self.assertEquals(self.writeitinstance1.mailit_template, template)

class MailSendingTestCase(TestCase):
    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 2')
        self.person3 = Person.objects.create(api_instance=self.api_instance2, name= 'Person 3')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact2 = Contact.objects.create(person=self.person2, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact3 = Contact.objects.create(person=self.person3, contact_type=self.contact_type1, value= 'test@test.com')
        self.writeitinstance1 = WriteItInstance.objects.create(name='instance 1', api_instance= self.api_instance1)
        self.writeitinstance2 = WriteItInstance.objects.create(name='instance 2', api_instance= self.api_instance2)
        self.message = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2])
        self.message2 = Message.objects.create(content = 'Content 1', subject='Subject 1', writeitinstance= self.writeitinstance2, persons = [self.person3])
        self.template1 = MailItTemplate.objects.create(writeitinstance=self.writeitinstance1,subject_template=u"subject %(subject)s %(content)s %(person)s",content_template=u"content %(subject)s %(content)s %(person)s")


    def test_sending_email(self):
        channel = MailChannel()
        result_of_sending = channel.send(self.message)

        self.assertTrue(result_of_sending)
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].subject, 'subject Subject 1 Content 1 Person 1')
        self.assertEquals(mail.outbox[0].body, 'content Subject 1 Content 1 Person 1')

    def test_it_fails_if_there_is_no_template(self):

        channel = MailChannel()
        result_of_sending = channel.send(self.message2)

        self.assertFalse(result_of_sending)


