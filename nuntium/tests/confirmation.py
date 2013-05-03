from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Confirmation
from nuntium.models import Message, WriteItInstance
from popit.models import Person
from contactos.models import Contact
from datetime import datetime
from plugin_mock.mental_message_plugin import MentalMessage


class ConfirmationTestCase(TestCase):
    def setUp(self):
        super(ConfirmationTestCase,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        marcel = Person.objects.all()[1]
        felipe = Person.objects.all()[2]
        self.channel = MentalMessage()
        self.mental_contact1 = Contact.objects.create(person=felipe, contact_type=self.channel.get_contact_type())

        self.message = Message.objects.create(content = 'hello there', subject='Wow!', writeitinstance= self.writeitinstance1, persons = [felipe])

    def test_creation(self):
        confirmation = Confirmation.objects.create(message=self.message)

        self.assertTrue(confirmation)
        self.assertEquals(confirmation.message, self.message)
        self.assertEquals(len(confirmation.key.strip()),32)
        self.assertTrue(isinstance(confirmation.created,datetime))
        self.assertTrue(confirmation.confirmated_at is None)


