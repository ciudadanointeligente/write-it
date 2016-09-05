from global_test_case import GlobalTestCase as TestCase
from django.db import IntegrityError
from django.db import models
from django.utils.translation import ugettext as _
from contactos.models import Contact, ContactType
from instance.models import WriteItInstance
from popolo_sources.models import PopoloSource
from ..models import Message, OutboundMessage, \
    MessageRecord, OutboundMessagePluginRecord, \
    OutboundMessageIdentifier, Answer, \
    NoContactOM, AbstractOutboundMessage
from django.contrib.sites.models import Site

from popolo.models import Person
from mock import patch
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from plugin_mock.mental_message_plugin import MentalMessage, FatalException, TryAgainException


class OutboundMessageTestCase(TestCase):
    def setUp(self):
        super(OutboundMessageTestCase, self).setUp()
        self.popolo_source = PopoloSource.objects.get(id=1)
        self.contact1 = Contact.objects.get(id=1)
        self.message = Message.objects.get(id=1)

    def test_create_a_outbound_message(self):
        outbound_message = OutboundMessage.objects.create(
            message=self.message,
            contact=self.contact1,
            site=Site.objects.get_current(),
            )
        # This means that there is a link between a contact and a message
        self.assertTrue(outbound_message)
        self.assertEquals(outbound_message.status, "new")

    def test_outbound_message_unicode(self):
        outbound_message = OutboundMessage.objects.create(
            message=self.message, contact=self.contact1, site=Site.objects.get_current())
        expected_unicode = _('%(subject)s sent to %(person)s (%(contact)s) at %(instance)s') % {
            'subject': self.message.subject,
            'person': self.contact1.person.name,
            'contact': self.contact1.value,
            'instance': self.message.writeitinstance.name,
            }
        self.assertEquals(outbound_message.__unicode__(), expected_unicode)

    def test_outbound_messsages_creation_on_message_save(self):
        """Creates an outbound message when a message is created"""
        message = Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="falvarez@votainteligente.cl",
            subject='Fiera es una perra feroz',
            writeitinstance=self.message.writeitinstance,
            persons=[self.contact1.person],
            )

        new_outbound_messages = OutboundMessage.objects.filter(message=message)

        self.assertEquals(new_outbound_messages.count(), 1)
        outbound_message = new_outbound_messages[0]
        self.assertEquals(outbound_message.contact, self.contact1)
        self.assertEquals(outbound_message.message, message)

    def test_successful_send(self):
        outbound_message = OutboundMessage.objects.create(
            message=self.message,
            contact=self.contact1,
            site=Site.objects.get_current(),
            )
        outbound_message.send()

        outbound_message = OutboundMessage.objects.get(id=outbound_message.id)
        self.assertEquals(outbound_message.status, "sent")

    def test_there_is_a_manager_that_retrieves_all_the_available_messages(self):
        outbound_message = OutboundMessage.objects.create(
            message=self.message,
            contact=self.contact1,
            status="ready",
            site=Site.objects.get_current(),
            )

        self.assertEquals(OutboundMessage.objects.to_send().filter(id=outbound_message.id).count(), 1)

    def test_create_a_new_outbound_message_identifier_on_creation(self):
        outbound_message = OutboundMessage.objects.create(
            message=self.message,
            contact=self.contact1,
            status="ready",
            site=Site.objects.get_current(),
            )
        identifier = OutboundMessageIdentifier.objects.get(outbound_message=outbound_message)

        self.assertTrue(identifier)

    def test_statuses(self):
        self.assertIn(("new", _("Newly created")), OutboundMessage.STATUS_CHOICES)
        self.assertIn(("ready", _("Ready to send")), OutboundMessage.STATUS_CHOICES)
        self.assertIn(("sent", _("Sent")), OutboundMessage.STATUS_CHOICES)
        self.assertIn(("error", _("Error sending it")), OutboundMessage.STATUS_CHOICES)
        self.assertIn(("needmodera", _("Needs moderation")), OutboundMessage.STATUS_CHOICES)


class OutboundMessageIdentifierTestCase(TestCase):
    def setUp(self):
        super(OutboundMessageIdentifierTestCase, self).setUp()
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.message = Message.objects.get(id=1)
        self.contact1 = Contact.objects.get(id=1)

    def test_create_an_outbound_message_identifier_when_creating_(self):
        with patch('uuid.uuid1') as string:
            string.return_value.hex = 'oliwi'
            outbound_message = OutboundMessage.objects.create(message=self.message, contact=self.contact1, site=Site.objects.get_current())
            identifier = OutboundMessageIdentifier.objects.get(outbound_message=outbound_message)
            string.assert_called()
            # the key is created when saved
            self.assertEquals(identifier.key, 'oliwi')

    def test_create_only_one_identifier_per_outbound_message(self):
        with self.assertRaises(IntegrityError):
            OutboundMessageIdentifier.objects.create(outbound_message=self.outbound_message)

    def test_the_key_does_not_change_on_save_twice(self):
        identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        expected_key = identifier.key

        identifier.save()

        self.assertEquals(expected_key, identifier.key)

    def test_create_an_answer_only_having_an_identifier(self):
        identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        answer_content = "La fiera no tiene pulgas."
        OutboundMessageIdentifier.create_answer(identifier.key, answer_content)
        the_person = self.outbound_message.contact.person
        the_answer = Answer.objects.get(message=self.outbound_message.message, person=the_person, content=answer_content)

        self.assertEquals(the_answer.content, answer_content)

    def test_create_an_answer_returns_the_answer_created(self):
        '''OutboundMessageIdentifier.create_answer returns an answer'''
        identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        answer_content = "La fiera no tiene pulgas."
        returned_answer = OutboundMessageIdentifier.create_answer(identifier.key, answer_content)
        the_person = self.outbound_message.contact.person
        the_answer = Answer.objects.get(message=self.outbound_message.message, person=the_person, content=answer_content)

        self.assertEquals(returned_answer, the_answer)

    def test_create_an_answer_with_content_html(self):
        '''OutboundMessageIdentifier.create_answer can receive a content_html field'''
        identifier = OutboundMessageIdentifier.objects.get(outbound_message=self.outbound_message)
        answer_content = u"La fiera no tiene pulgas."
        answer_content_html = u'<p>La fiera no tiene pulgas.</p>'

        returned_answer = OutboundMessageIdentifier.create_answer(identifier.key,
            answer_content,
            content_html=answer_content_html)

        self.assertEquals(returned_answer.content_html, answer_content_html)


class PluginMentalMessageTestCase(TestCase):
    '''
    This testcase is going to be used as an example for the creation
    of new plugins MentalMessage is the plugin for sending messages in
    a telepathic way
    '''
    def setUp(self):
        super(PluginMentalMessageTestCase, self).setUp()
        self.outbound_message = OutboundMessage.objects.get(id=1)
        self.message = Message.objects.get(id=1)
        self.message_type = ContentType.objects.get(id=1)
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.channel = MentalMessage()
        self.user = User.objects.get(id=1)
        self.mental_contact1 = Contact.objects.create(
            person=self.person1,
            contact_type=self.channel.get_contact_type(),
            writeitinstance=self.writeitinstance1
            )

    def test_it_only_sends_messages_to_contacts_of_the_same_channel(self):
        otubound_message = OutboundMessage.objects.create(contact=self.mental_contact1, message=self.message, site=Site.objects.get_current())
        otubound_message.send()

        record = OutboundMessagePluginRecord.objects.get(outbound_message=otubound_message)
        self.assertEquals(record.plugin, self.channel.get_model())

    def test_it_has_a_send_method_and_does_whatever(self):
        # it sends the message
        self.channel.send(self.outbound_message)
        # And I'm gonna prove it by testing that a new record was created
        the_records = MessageRecord.objects.filter(object_id=self.outbound_message.id, status="sent using mental messages")
        self.assertEquals(the_records.count(), 1)
        # It should send using all the channels available

    def test_it_should_create_a_new_kind_of_outbox_message(self):
        otubound_message = OutboundMessage.objects.create(contact=self.mental_contact1, message=self.message, site=Site.objects.get_current())
        otubound_message.send()
        the_records = MessageRecord.objects.filter(
            object_id=otubound_message.id,
            status="sent using mental messages",
            )
        self.assertEquals(the_records.count(), 1)

    def test_fatal_exception_when_sending_a_mental_message(self):
        '''
        This type of error is when there is not much to do, like an inexisting email address
        and in Mental message it raises a fatal error when you send the message RaiseFatalErrorPlz
        '''
        with self.assertRaises(FatalException):
            self.channel.send_mental_message("RaiseFatalErrorPlz")

    def test_non_fatal_exception(self):
        with self.assertRaises(TryAgainException):
            self.channel.send_mental_message("RaiseTryAgainErrorPlz")

    def test_it_raises_an_error_when_sending_error_in_the_subject(self):
        # this is a test for when you send a message with RaiseFatalErrorPlz in subject then is going
        # to raise an exception

        error_message = Message.objects.create(
            content='Content 1',
            subject='RaiseFatalErrorPlz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        outbound_message = OutboundMessage.objects.filter(message=error_message)[0]
        result = self.channel.send(outbound_message)
        successfully_sent = result[0]
        fatal_error = result[1]

        self.assertFalse(successfully_sent)
        self.assertTrue(fatal_error)

    def test_non_fatal_error_keeps_outbound_message_status_as_ready(self):
        '''
        This type of error is a soft error, like someone having full inbox and we should retry
        sending the message
        '''
        error_message = Message.objects.create(
            content='Content 1',
            subject='RaiseTryAgainErrorPlz',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        outbound_message = OutboundMessage.objects.filter(message=error_message)[0]
        result = self.channel.send(outbound_message)
        successfully_sent = result[0]
        fatal_error = result[1]

        self.assertFalse(successfully_sent)
        self.assertFalse(fatal_error)

    def test_success_sending_a_message(self):
        error_message = Message.objects.create(
            content='Content 1',
            subject='Come on! send me!',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )
        outbound_message = OutboundMessage.objects.filter(message=error_message)[0]
        result = self.channel.send(outbound_message)
        successfully_sent = result[0]
        fatal_error = result[1]

        self.assertTrue(successfully_sent)
        self.assertTrue(fatal_error is None)

    def test_plugin_gets_contact_type(self):
        """From a plugin I can get its contact type"""
        the_mental_channel = MentalMessage()
        contact_type = the_mental_channel.get_contact_type()

        self.assertEquals(contact_type.label_name, "The Mind")
        self.assertEquals(contact_type.name, "mind")


class AbstractOutboundMessageTestCase(TestCase):
    def setUp(self):
        super(AbstractOutboundMessageTestCase, self).setUp()
        self.message = Message.objects.get(id=1)

    def test_create_an_abstract_class(self):
        """ Create a subclass of abstract class that does not contain contact"""
        class ImplementationThing(AbstractOutboundMessage):
            pass

        implementation = ImplementationThing(message=self.message)
        # This means that there is a link between a contact and a message
        self.assertTrue(implementation)
        self.assertIsInstance(implementation, models.Model)
        self.assertEquals(implementation.status, "new")
        self.assertEquals(implementation.message, self.message)

    def test_abstract_is_acctually_abstract(self):
        """The class is actually abstract"""
        self.assertTrue(AbstractOutboundMessage._meta.abstract)
        # OK this is a total redunduncy but how else can I test this?


class MessagesToPersonWithoutContactsTestCase(TestCase):
    def setUp(self):
        super(MessagesToPersonWithoutContactsTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.message = Message.objects.get(id=1)
        self.people = self.message.people
        for person in self.people:
            person.contact_set.all().delete()

    def test_create_concrete_class(self):
        """Creating a class that holds outbound messages for people without contact"""
        pedro = self.people[0]

        no_contact_outbound_message = NoContactOM.objects.create(
            message=self.message,
            person=pedro,
            site=Site.objects.get_current(),
            )
        self.assertTrue(no_contact_outbound_message)
        self.assertEquals(no_contact_outbound_message.message, self.message)
        self.assertIsInstance(no_contact_outbound_message, AbstractOutboundMessage)
        self.assertFalse(hasattr(no_contact_outbound_message, 'contact'))

    def test_automatically_creates_no_contact_outbound_messages(self):
        """ When sending a message to people without contacts it creates NoContactOM"""
        message = Message.objects.create(
            content='Content 1',
            subject='RaiseFatalErrorPlz',
            writeitinstance=self.writeitinstance,
            persons=[person for person in self.people],
            )

        outbound_messages = OutboundMessage.objects.filter(message=message)
        self.assertFalse(outbound_messages)
        no_contact_om = NoContactOM.objects.filter(message=message)
        self.assertEquals(no_contact_om.count(), self.people.count())
        for person in self.people:
            self.assertTrue(no_contact_om.get(person=person))

    def test_people_is_included_in_people(self):
        """It let's you do message.people with people without contacts"""
        persons_in_message = [person for person in self.people]
        message = Message.objects.create(
            content='Content 1',
            subject='RaiseFatalErrorPlz',
            writeitinstance=self.writeitinstance,
            persons=persons_in_message,
            )

        self.assertEquals(message.people.count(), len(persons_in_message))
        for person in persons_in_message:
            self.assertTrue(message.people.get(id=person.id))
# When adding a new contact for a person without contacts
# then it should send a message to them
# and in technical terms it means that it should create outbound_messages
# with the contact and in status "new"

    def test_create_outbound_messages_on_new_contact(self):
        '''Create new outbound_messages when a new contact is created'''
        persons_in_message = [person for person in self.people]
        peter = self.people[0]
        message = Message.objects.create(
            content='Content 1',
            subject='RaiseFatalErrorPlz',
            writeitinstance=self.writeitinstance,
            persons=persons_in_message,
            )

        email = ContactType.objects.get(id=1)
        contact_for_peter = Contact.objects.create(
            person=peter,
            value="peter@votainteligente.cl",
            contact_type=email,
            writeitinstance=self.writeitinstance,
            )

        outbound_messages = OutboundMessage.objects.filter(message=message)
        no_contact_om = NoContactOM.objects.filter(message=message, person=peter)

        self.assertFalse(no_contact_om)
        self.assertTrue(outbound_messages)
        self.assertEquals(len(outbound_messages), 1)
        om = outbound_messages[0]
        self.assertEquals(om.contact, contact_for_peter)
        self.assertEquals(om.status, "new")

    def test_it_copies_the_status_of_the_outbound_message(self):
        """If there is already a NoContactOM it brings the status to the new outbound message"""
        persons_in_message = [person for person in self.people]
        peter = self.people[0]
        message = Message.objects.create(
            content='Content 1',
            subject='aaa',
            writeitinstance=self.writeitinstance,
            persons=persons_in_message,
            )

        message.recently_confirmated()

        outbound_message_to_peter = NoContactOM.objects.get(
            message=message,
            person=peter,
            )

        self.assertEquals(outbound_message_to_peter.status, 'ready')

    def test_it_copies_the_status_to_the_new_outbound_message_when_creating_a_new_contact(self):
        """When we create a new contact after changing the status it creates OM with that status"""
        persons_in_message = [person for person in self.people]
        peter = self.people[0]
        message = Message.objects.create(
            content='Content 1',
            subject='aaa',
            writeitinstance=self.writeitinstance,
            persons=persons_in_message,
            )

        message.recently_confirmated()

        email = ContactType.objects.get(id=1)
        contact_for_peter = Contact.objects.create(
            person=peter,
            value="peter@votainteligente.cl",
            contact_type=email,
            writeitinstance=self.writeitinstance,
            )

        outbound_message = OutboundMessage.objects.get(
            message=message,
            contact=contact_for_peter,
            )

        self.assertEquals(outbound_message.status, "ready")
