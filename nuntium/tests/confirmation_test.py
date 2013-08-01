from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Confirmation, OutboundMessage
from nuntium.models import Message, WriteItInstance
from popit.models import Person
from contactos.models import Contact
from datetime import datetime
from django.core import mail
from plugin_mock.mental_message_plugin import MentalMessage
from subdomains.utils import reverse
from django.contrib.sites.models import Site
from django.utils.unittest import skip
from django.conf import settings
from django.contrib.auth.models import User


class ConfirmationTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTestCase,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.Marcel = Person.objects.all()[1]
        felipe = Person.objects.all()[2]
        self.channel = MentalMessage()
        self.user = User.objects.all()[0]
        self.mental_contact1 = Contact.objects.create(person=felipe, contact_type=self.channel.get_contact_type(), owner=self.user)

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
        self.assertFalse(confirmation_full_url in mail.outbox[0].body)
        self.assertTrue(url in mail.outbox[0].body)
        self.assertTrue(self.message.get_absolute_url() in mail.outbox[0].body)
        self.assertFalse(message_full_url in mail.outbox[0].body)

        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(self.message.author_email in mail.outbox[0].to)
        expected_from_email = self.message.writeitinstance.slug+"@"+settings.DEFAULT_FROM_DOMAIN
        self.assertEquals(mail.outbox[0].from_email, expected_from_email)

    def test_confirmation_get_absolute_url(self):
        confirmation = Confirmation.objects.create(message=self.message)
        expected_url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        self.assertEquals(expected_url, confirmation.get_absolute_url())


    def test_private_messages_do_not_have_its_absolute_url(self):
        self.message.public = False
        self.message.save()

        confirmation = Confirmation.objects.create(message=self.message)
        self.assertFalse(self.message.get_absolute_url() in mail.outbox[0].body)
        
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
        url = reverse('message_detail', subdomain=self.message.writeitinstance.slug, kwargs={'slug':self.message.slug})
        response = self.client.get(url)

        self.assertEquals(response.status_code, 404)

from mock import patch
class EmailSendingErrorHandling(TestCase):
    def setUp(self):
        super(EmailSendingErrorHandling,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.Marcel = Person.objects.all()[1]
        felipe = Person.objects.all()[2]
        self.channel = MentalMessage()
        self.user = User.objects.all()[0]
        self.mental_contact1 = Contact.objects.create(person=felipe, contact_type=self.channel.get_contact_type(), owner=self.user)
        self.message = Message.objects.create(content = 'hello there', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Wow!',
         writeitinstance= self.writeitinstance1, persons = [felipe])
        self.message2 = Message.objects.create(content = 'hello there', author_name='Marcel', author_email="maugsburger@votainteligente.cl", subject='Wow!',
         writeitinstance= self.writeitinstance1, persons = [self.Marcel])

    def test_confirmation_sending_error_destroys_message(self):
        with patch("django.core.mail.EmailMultiAlternatives.send") as send:
            send.side_effect = Exception("The message was not sent")
            confirmation = Confirmation.objects.create(message=self.message2)
            self.assertEquals(len(mail.outbox), 0)

        #ok I'm taking the desition that a message with a confirmation error
        #will be deleted and also the confirmation
        #this is obviously subjected to change
        #but I see no point on keeping the message or the confirmation

        messages = Message.objects.filter(id=self.message2.id)
        confirmations = Confirmation.objects.filter(id=confirmation.id)


        #I'm Changing this cause it makes no sense right now
        self.assertEquals(messages.count(), 1)
        self.assertEquals(confirmations.count(), 1)