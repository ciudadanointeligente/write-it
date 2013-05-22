from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Confirmation, OutboundMessage
from nuntium.models import Message, WriteItInstance
from popit.models import Person
from contactos.models import Contact
from datetime import datetime
from django.core import mail
from plugin_mock.mental_message_plugin import MentalMessage
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.unittest import skip


class ConfirmationTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTestCase,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.Marcel = Person.objects.all()[1]
        felipe = Person.objects.all()[2]
        self.channel = MentalMessage()
        self.mental_contact1 = Contact.objects.create(person=felipe, contact_type=self.channel.get_contact_type())

        self.message = Message.objects.create(content = 'hello there', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Wow!',
         writeitinstance= self.writeitinstance1, persons = [felipe])
        self.message2 = Message.objects.create(content = 'hello there', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Wow!',
         writeitinstance= self.writeitinstance1, persons = [self.Marcel])

    def test_instanciate(self):
        confirmation = Confirmation(message=self.message)
        self.assertTrue(confirmation)
        self.assertEquals(len(confirmation.key.strip()),0)

    def test_creation_and_save(self):
        confirmation = Confirmation.objects.create(message=self.message)

        self.assertTrue(confirmation.id)
        self.assertEquals(confirmation.message, self.message)
        self.assertEquals(len(confirmation.key.strip()),32)
        self.assertTrue(isinstance(confirmation.created,datetime))
        self.assertTrue(confirmation.confirmated_at is None)

    def test_confirmation_has_a_key_generator(self):
        key1 = Confirmation.key_generator()
        key2 = Confirmation.key_generator()

        self.assertNotEquals(key1, key2)

    def test_duplication(self):
        #Serioulsly I'm getting to many times Duplicate entry for key 'key'
        confirmation1 = Confirmation.objects.create(message=self.message)
        confirmation2 = Confirmation.objects.create(message=self.message2)


        self.assertNotEquals(confirmation1.key, confirmation2.key)


    def test_it_sends_an_email_to_the_author_asking_for_confirmation(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        current_site = Site.objects.get_current()
        confirmation_full_url = "http://"+current_site.domain+url

        message_full_url = 'http://'+current_site.domain+self.message.get_absolute_url()

        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, 'Confirmation email for a message in WriteIt')
        self.assertTrue(self.message.author_name in mail.outbox[0].body)
        self.assertTrue(confirmation_full_url in mail.outbox[0].body)
        self.assertTrue(message_full_url in mail.outbox[0].body)

        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(self.message.author_email in mail.outbox[0].to)


    def test_access_the_confirmation_url(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/confirm.html')

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
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        response1 = self.client.get(url)
        response2 = self.client.get(url)


        self.assertEquals(response1.status_code, 200)
        self.assertEquals(response2.status_code, 404)

    def test_i_cannot_access_a_non_confirmed_message(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse('message_detail', kwargs={'slug':self.message.slug})
        response = self.client.get(url)

        self.assertEquals(response.status_code, 404)

from ludibrio import Stub, Mock
from ludibrio.matcher import *
class EmailSendingErrorHandling(TestCase):
    def setUp(self):
        super(EmailSendingErrorHandling,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.Marcel = Person.objects.all()[1]
        felipe = Person.objects.all()[2]
        self.channel = MentalMessage()
        self.mental_contact1 = Contact.objects.create(person=felipe, contact_type=self.channel.get_contact_type())
        self.message = Message.objects.create(content = 'hello there', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Wow!',
         writeitinstance= self.writeitinstance1, persons = [felipe])
        self.message2 = Message.objects.create(content = 'hello there', author_name='Marcel', author_email="maugsburger@votainteligente.cl", subject='Wow!',
         writeitinstance= self.writeitinstance1, persons = [self.Marcel])

    def test_confirmation_sending_error_destroys_message(self):
        
        with Stub() as email_sending:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(any(), 
                any(),#content
                any(),#From
                ['maugsburger@votainteligente.cl']#To
                )
            msg.attach_alternative(any(), "text/html")
            msg.send() >> Exception("The message was not sent")


        

        confirmation = Confirmation.objects.create(message=self.message2)
        email_sending.restore_import()
        
        #
        self.assertEquals(len(mail.outbox), 0)



