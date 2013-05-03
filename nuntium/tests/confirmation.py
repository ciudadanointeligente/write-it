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

    def test_creation(self):
        confirmation = Confirmation.objects.create(message=self.message)

        self.assertTrue(confirmation)
        self.assertEquals(confirmation.message, self.message)
        self.assertEquals(len(confirmation.key.strip()),32)
        self.assertTrue(isinstance(confirmation.created,datetime))
        self.assertTrue(confirmation.confirmated_at is None)

    def test_it_sends_an_email_to_the_author_asking_for_confirmation(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        current_site = Site.objects.get_current()
        confirmation_full_url = "http://"+current_site.domain+url

        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, 'Confirmation email for a message in WriteIt')
        self.assertTrue(self.message.author_name in mail.outbox[0].body)
        self.assertTrue(confirmation_full_url in mail.outbox[0].body)

        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(self.message.author_email in mail.outbox[0].to)


    def test_access_the_confirmation_url(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'nuntium/confirm.html')

        confirmation = Confirmation.objects.get(id=confirmation.id)
        self.assertTrue(confirmation.confirmated_at is not None)
        outbound_messages = OutboundMessage.objects.filter(message=confirmation.message)

        self.assertEquals(outbound_messages[0].status, "ready")


    def test_it_does_not_confirm_twice(self):
        confirmation = Confirmation.objects.create(message=self.message)
        url = reverse('confirm', kwargs={
            'slug':confirmation.key
            })
        response1 = self.client.get(url)
        response2 = self.client.get(url)


        self.assertEquals(response1.status_code, 200)
        self.assertEquals(response2.status_code, 404)