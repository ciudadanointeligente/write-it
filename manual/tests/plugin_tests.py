from global_test_case import GlobalTestCase as TestCase
from contactos.models import ContactType
from .. import ManualChannel
from django.utils.unittest import skip
from django.core import mail
from nuntium.models import WriteItInstance, OutboundMessage, Message
from contactos.models import Contact
from nuntium.plugins import OutputPlugin

class ManualPluginTestCase(TestCase):
    def setUp(self):
        super(ManualPluginTestCase, self).setUp()

    def test_instanciate_the_plugin(self):
        '''Instanciate the manual plugin'''
        channel = ManualChannel()
        self.assertTrue(channel)
        self.assertIsInstance(channel, OutputPlugin)


    def test_it_has_a_contact_type(self):
        '''It has a manual contact type'''
        channel = ManualChannel()
        contact_type = channel.get_contact_type()
        self.assertIsInstance(contact_type, ContactType)
        self.assertEquals(contact_type.label_name, "Manual Contact")
        self.assertEquals(contact_type.name, "manual")


    def test_has_a_send_method(self):
        '''It does have a send method'''
        channel = ManualChannel()
        self.assertTrue(channel.send)



class ManualSendingTestCase(TestCase):
    def setUp(self):
        super(ManualSendingTestCase, self).setUp()
        self.channel = ManualChannel()
        self.writeitinstance = WriteItInstance.objects.all()[0]
        self.person = self.writeitinstance.persons.all()[0]
        self.message = Message.objects.all()[0]
        self.outbound_message1 = OutboundMessage.objects.filter(message=self.message)[0]

    @skip('Not doing it for now')
    def test_sending_a_manual_message(self):
        '''
        Sending a message manually is done to the owner of the instance
        '''
        
        contact = Contact.objects.create(
            owner = self.writeitinstance.owner,
            person = self.person,
            contact_type = self.channel.get_contact_type(),
            value=""
            )

        result_of_sending, fatal_error = self.channel.send(self.outbound_message1)
        self.assertTrue(result_of_sending)
        self.assertTrue(fatal_error is None)
        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertEquals(mail.outbox[0].subject, '[WriteIT] Message: Subject 1')
