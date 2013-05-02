from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord
from popit.models import Person, ApiInstance
from django.contrib.contenttypes.models import ContentType

class OutboundMessageTestCase(TestCase):
    def setUp(self):
        super(OutboundMessageTestCase,self).setUp()
        self.api_instance1 = ApiInstance.objects.all()[0]
        self.contact1 = Contact.objects.all()[0]
        self.message = Message.objects.all()[0]


    def test_create_a_outbound_message(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        #This means that there is a link between a contact and a message
        self.assertTrue(outbound_message)
        self.assertEquals(outbound_message.status, "ready")


    def test_outbound_message_unicode(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        expected_unicode = _('%(subject)s sent to %(person)s (%(contact)s) at %(instance)s') % {
            'subject': self.message.subject,
            'person':self.contact1.person.name,
            'contact':self.contact1.value,
            'instance':self.message.writeitinstance.name
        }
        self.assertEquals(outbound_message.__unicode__(), expected_unicode)

    def test_outbound_messsages_creation_on_message_save(self):
        # si new message then x neew outbound TestMessages
        new_outbound_messages = OutboundMessage.objects.all()
        self.assertEquals(new_outbound_messages.count(), 2)


    def test_successful_send(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)
        outbound_message.send()

        outbound_message = OutboundMessage.objects.get(id=outbound_message.id)
        self.assertEquals(outbound_message.status, "sent")


    @skip("There should be a link between a message and a person that now does not exist")
    def test_it_should_create_an_output_message_for_person_without_contacts(self):
        person_without_contacts = Person.objects.create(api_instance=self.api_instance1, name= 'I don\'t have any contacts')
        message_to_3 = Message.objects.create(content = 'hello there', subject='Wow!', writeitinstance= self.writeitinstance1, persons = [self.person1,\
            self.person2, person_without_contacts])

        outbound_messages = OutboundMessage.objects.filter(message=message_to_3)
        self.assertEquals(outbound_messages.count(), 3)


    def test_there_is_a_manager_that_retrieves_all_the_available_messages(self):
        outbound_message = OutboundMessage.objects.create(message = self.message, contact=self.contact1)

        self.assertEquals(OutboundMessage.objects.to_send().filter(id=outbound_message.id).count(),1)


from plugin_mock.mental_message_plugin import MentalMessage, FatalException, TryAgainException
class PluginMentalMessageTestCase(TestCase):
    '''
    This testcase is going to be used as an example for the creation
    of new plugins MentalMessage is the plugin for sending messages in
    a telepathic way
    '''
    def setUp(self):
        super(PluginMentalMessageTestCase,self).setUp()
        self.outbound_message = OutboundMessage.objects.all()[0]
        self.message_type = ContentType.objects.all()[0]
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]


    def test_it_has_a_send_method_and_does_whatever(self):
        the_mental_channel = MentalMessage()
        #it sends the message
        the_mental_channel.send(self.outbound_message)
        #And I'm gonna prove it by testing that a new record was created
        the_records = MessageRecord.objects.filter(object_id=self.outbound_message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(),1)
        #It should send using all the channels available

    def test_it_should_create_a_new_kind_of_outbox_message(self):
        self.outbound_message.send()
        the_records = MessageRecord.objects.filter(object_id=self.outbound_message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(),1)

    def test_fatal_exception_when_sending_a_mental_message(self):
        '''
        This type of error is when there is not much to do, like an inexisting email address
        and in Mental message it raises a fatal error when you send the message RaiseFatalErrorPlz
        '''
        the_mental_channel = MentalMessage()
        with self.assertRaises(FatalException) as cm:
            the_mental_channel.send_mental_message("RaiseFatalErrorPlz")

    def test_non_fatal_exception(self):
        the_mental_channel = MentalMessage()
        with self.assertRaises(TryAgainException) as cm:
            the_mental_channel.send_mental_message("RaiseTryAgainErrorPlz")

    def test_it_raises_an_error_when_sending_error_in_the_subject(self):
        #this is a test for when you send a message with RaiseFatalErrorPlz in subject then is going
        #to raise an exception
        

        error_message = Message.objects.create(content = 'Content 1', subject='RaiseFatalErrorPlz', 
            writeitinstance= self.writeitinstance1, persons = [self.person1])
        outbound_message = OutboundMessage.objects.filter(message=error_message)[0]

        the_mental_channel = MentalMessage()
        result = the_mental_channel.send(outbound_message)
        successfully_sent = result[0]
        fatal_error = result[1]

        self.assertFalse(successfully_sent)
        self.assertTrue(fatal_error)



    def test_non_fatal_error_keeps_outbound_message_status_as_ready(self):
        '''
        This type of error is a soft error, like someone having full inbox and we should retry
        sending the message
        '''
        error_message = Message.objects.create(content = 'Content 1', subject='RaiseTryAgainErrorPlz', 
            writeitinstance= self.writeitinstance1, persons = [self.person1])
        outbound_message = OutboundMessage.objects.filter(message=error_message)[0]

        the_mental_channel = MentalMessage()
        result = the_mental_channel.send(outbound_message)
        successfully_sent = result[0]
        fatal_error = result[1]

        self.assertFalse(successfully_sent)
        self.assertFalse(fatal_error)


    def test_success_sending_a_message(self):
        '''
        '''
        error_message = Message.objects.create(content = 'Content 1', subject='Come on! send me!', 
            writeitinstance= self.writeitinstance1, persons = [self.person1])
        outbound_message = OutboundMessage.objects.filter(message=error_message)[0]

        the_mental_channel = MentalMessage()
        result = the_mental_channel.send(outbound_message)
        successfully_sent = result[0]
        fatal_error = result[1]


        self.assertTrue(successfully_sent)
        self.assertTrue(fatal_error is None)

