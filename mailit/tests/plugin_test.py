from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from mailit import MailChannel
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from nuntium.plugins import OutputPlugin
from mailit.models import MailItTemplate
from django.core import mail
from django.contrib.auth.models import User
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
        self.owner = User.objects.all()[0]
        self.content_template = ''
        with open('mailit/templates/mailit/mails/content_template.txt', 'r') as f:
            self.content_template += f.read()

    def test_it_has_a_template(self):
        self.writeitinstance2.mailit_template.delete()
        template = MailItTemplate.objects.create(writeitinstance=self.writeitinstance2,subject_template=u"hello somebody %(thing)s",content_template=u"content thing %(another)s asdas")

        self.assertTrue(template)
        self.assertEquals(self.writeitinstance2.mailit_template, template)


    def test_mailit_template_has_some_default_data(self):
        self.writeitinstance2.mailit_template.delete()


        
        template = MailItTemplate.objects.create(writeitinstance=self.writeitinstance2)

        self.assertEquals(template.subject_template, "[WriteIT] Message: %(subject)s")
        self.assertEquals(template.content_template, self.content_template)

    def test_when_creating_a_new_instance_then_a_new_template_is_created_automatically(self):
        instance  = WriteItInstance.objects.create(name='instance 234', slug='instance-234', owner=self.owner)

        self.assertTrue(instance.mailit_template)
        self.assertEquals(instance.mailit_template.subject_template, "[WriteIT] Message: %(subject)s")
        self.assertEquals(instance.mailit_template.content_template, self.content_template)

    def test_it_only_creates_templates_when_creating_not_when_updating(self):
        instance  = WriteItInstance.objects.create(name='instance 234', slug='instance-234', owner=self.owner)


        instance.save()

        self.assertTrue(instance.mailit_template)
        self.assertEquals(instance.mailit_template.subject_template, "[WriteIT] Message: %(subject)s")
        self.assertEquals(instance.mailit_template.content_template, self.content_template)

class MailSendingTestCase(TestCase):
    def setUp(self):
        super(MailSendingTestCase,self).setUp()
        self.person3 = Person.objects.all()[2]
        self.channel = MailChannel()
        self.contact_type2 = ContactType.objects.create(name= 'Uninvented one',label_name='bzbzbzb')
        self.user = User.objects.all()[0]
        self.contact3 = Contact.objects.create(
            person=self.person3, 
            contact_type=self.channel.get_contact_type(), 
            value= '123456789',
            owner=self.user)
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.writeitinstance2 = WriteItInstance.objects.all()[1]
        self.message = Message.objects.all()[0]
        self.outbound_message1 = OutboundMessage.objects.filter(message=self.message)[0]
        self.message_to_another_contact = Message.objects.create(content = 'Content 1', 
            subject='Subject 1', writeitinstance= self.writeitinstance2, persons = [self.person3])
        self.outbound_message2 = OutboundMessage.objects.filter(message=self.message_to_another_contact)[0]

        self.template1 = MailItTemplate.objects.all()[0]


    def test_sending_email(self):
        
        result_of_sending, fatal_error = self.channel.send(self.outbound_message1)

        self.assertTrue(result_of_sending)
        self.assertTrue(fatal_error is None)
        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, 'WriteIT Message: Subject 1')
        self.assertEquals(mail.outbox[0].body, u'Hello Pedro:\r\nYou have a new message:\r\nsubject: Subject 1 \r\ncontent: Content 1\r\n\r\nSeeya\r\n--\r\nYou writeIt and we deliverit.')
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertIn("pdaire@ciudadanointeligente.org", mail.outbox[0].to)



    def test_sending_from_email_expected_from_email(self):
        result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
        author_name = self.outbound_message1.message.author_name
        expected_from_email = author_name+" <"+self.outbound_message1.message.writeitinstance.slug+"+"+self.outbound_message1.outboundmessageidentifier.key\
                                +'@'+settings.DEFAULT_FROM_DOMAIN+">"
        self.assertEquals(mail.outbox[0].from_email, expected_from_email)

    def test_send_email_logs(self):
        author_name = self.outbound_message1.message.author_name
        from_email = author_name+" <"+self.outbound_message1.message.writeitinstance.slug+"+"+self.outbound_message1.outboundmessageidentifier.key\
                                +'@'+settings.DEFAULT_FROM_DOMAIN+">"
        with patch('logging.info') as info:
            expected_log = "Mail sent from %(from)s to %(to)s" % {
            'from' : from_email,
            'to' : "pdaire@ciudadanointeligente.org"
            }
            self.channel.send(self.outbound_message1)

            info.assert_called_with(expected_log)

    def test_it_fails_if_there_is_no_template(self):
        result_of_sending, fatal_error = self.channel.send(self.message_to_another_contact)

        self.assertFalse(result_of_sending)
        self.assertFalse(fatal_error)


    def test_it_only_sends_mails_to_email_contacts(self):
        template = self.writeitinstance2.mailit_template
        contact3 = Contact.objects.create(person=self.person3, contact_type=self.contact_type2,
            value= 'person1@votainteligente.cl',
            owner=self.user)
        message = Message.objects.create(content="The content", subject="the subject",
            writeitinstance=self.writeitinstance2, persons = [self.person3],
            )

        outbound_message = OutboundMessage.objects.get(message=message,
                                                        contact=contact3
            )
        
        result_of_sending = outbound_message.send()
        self.assertEquals(len(mail.outbox), 0)#because none has been sent


    def test_template_string_keys(self):

        template = self.writeitinstance2.mailit_template
        contact3 = Contact.objects.create(person=self.person3, contact_type=self.channel.get_contact_type(),
            value= 'person1@votainteligente.cl',
            owner=self.user)
        message = Message.objects.create(content="The content", subject="the subject",
            writeitinstance=self.writeitinstance2, persons = [self.person3],author_name="Felipe",
            author_email="falvarez@votainteligente.cl"
            )
        outbound_message = OutboundMessage.objects.get(message=message,
                                                        contact=contact3
            )
        result = outbound_message.send()


        self.assertTrue(message.author_name in mail.outbox[0].body)
        self.assertTrue(message.author_email not in mail.outbox[0].body)
        self.assertIn(self.writeitinstance2.get_absolute_url(), mail.outbox[0].body)

from smtplib import SMTPRecipientsRefused, SMTPServerDisconnected, SMTPResponseException
from mock import patch
class SmtpErrorHandling(TestCase):
    def setUp(self):
        super(SmtpErrorHandling, self).setUp()
        self.outbound_message1 = OutboundMessage.objects.all()[0]
        self.channel = MailChannel()


    def test_server_disconnected(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPServerDisconnected

        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPServerDisconnected()
            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            self.assertFalse(result_of_sending)
            self.assertFalse(fatal_error)

    def test_smpt_error_code_500(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(500,"")
            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

        #I'm not sure if this kind of error is definitive but
        #I'm taking it as if we should not try to send this
        #message again, but for example

    def test_any_other_exception(self):
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = Exception(401,"Something very bad")
            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

    def test_smpt_error_code_501(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException

        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(501,"")

            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
        

            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

    def test_smpt_error_code_502(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(502,"")
            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            

            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

    def test_smpt_error_code_503(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException

        with patch("django.core.mail.send_mail") as send_mail:

            send_mail.side_effect = SMTPResponseException(503,"")

            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            

            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)
        
    def test_smpt_error_code_504(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(504,"")

            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            

            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

    def test_smpt_error_code_550(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(550,"")

            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            

            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

    def test_smpt_error_code_551(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(551,"")

            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            

            self.assertFalse(result_of_sending)
            self.assertTrue(fatal_error)

    def test_smpt_error_code_552(self):
        #to handle this kind of error
        #http://docs.python.org/2.7/library/smtplib.html#smtplib.SMTPResponseException
        with patch("django.core.mail.send_mail") as send_mail:
            send_mail.side_effect = SMTPResponseException(552,"")

            result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
            

            self.assertFalse(result_of_sending)
            self.assertFalse(fatal_error)
        









