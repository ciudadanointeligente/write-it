from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from mailit import MailChannel
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from nuntium.plugins import OutputPlugin
from mailit.models import MailItTemplate
from django.core import mail
from django.conf import settings

class MailChannelTestCase(TestCase):

    def setUp(self):
        super(MailChannelTestCase,self).setUp()

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
        super(MailTemplateTestCase,self).setUp()
        self.writeitinstance2 = WriteItInstance.objects.all()[1]#the other one already has a template

    def test_it_has_a_template(self):
        template = MailItTemplate.objects.create(writeitinstance=self.writeitinstance2,subject_template=u"hello somebody %(thing)s",content_template=u"content thing %(another)s asdas")

        self.assertTrue(template)
        self.assertEquals(self.writeitinstance2.mailit_template, template)

class MailSendingTestCase(TestCase):
    def setUp(self):
        super(MailSendingTestCase,self).setUp()
        self.person3 = Person.objects.all()[2]
        self.contact_type2 = ContactType.objects.create(name= 'Uninvented one',label_name='bzbzbzb')
        self.contact3 = Contact.objects.create(person=self.person3, contact_type=self.contact_type2, value= '123456789')
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.writeitinstance2 = WriteItInstance.objects.all()[1]
        self.message = Message.objects.all()[0]
        self.outbound_message1 = OutboundMessage.objects.filter(message=self.message)[0]
        self.message_to_another_contact = Message.objects.create(content = 'Content 1', 
            subject='Subject 1', writeitinstance= self.writeitinstance2, persons = [self.person3])
        self.outbound_message2 = OutboundMessage.objects.get(message=self.message_to_another_contact)
        self.template1 = MailItTemplate.objects.all()[0]


    def test_sending_email(self):
        channel = MailChannel()
        result_of_sending, fatal_error = channel.send(self.outbound_message1)

        self.assertTrue(result_of_sending)
        self.assertTrue(fatal_error is None)
        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, 'WriteIT Message: Subject 1')
        self.assertEquals(mail.outbox[0].body, u'Hello Pedro:\r\nYou have a new message:\r\nsubject: Subject 1 \r\ncontent: Content 1\r\n\r\nSeeya\r\n--\r\nYou writeIt and we deliverit.')
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue("pdaire@ciudadanointeligente.org" in mail.outbox[0].to)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_it_fails_if_there_is_no_template(self):
        channel = MailChannel()
        result_of_sending, fatal_error = channel.send(self.message_to_another_contact)

        self.assertFalse(result_of_sending)
        self.assertFalse(fatal_error)


    def test_it_only_sends_mails_to_email_contacts(self):
        template = MailItTemplate.objects.create(writeitinstance=self.writeitinstance2
            ,subject_template=u"subject %(subject)s %(content)s %(person)s",
            content_template=u"content %(subject)s %(content)s %(person)s")
        message = Message.objects.create(content="The content", subject="the subject",
            writeitinstance=self.writeitinstance2, persons = [self.person3],
            )
        channel = MailChannel()
        result_of_sending = channel.send(message)

        self.assertTrue(result_of_sending)
        self.assertEquals(len(mail.outbox), 0)#because none has been sent





