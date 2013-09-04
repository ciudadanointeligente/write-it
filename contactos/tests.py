from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from contactos.models import ContactType, Contact
from popit.models import Person, ApiInstance
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core import mail
from django.conf import settings
from nuntium.models import OutboundMessage

class ContactTestCase(TestCase):
    def setUp(self):
        super(ContactTestCase,self).setUp()
        self.person = Person.objects.all()[0]
        self.user = User.objects.all()[0]

    def test_create_contact_type(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        self.assertTrue(contact_type)
        self.assertEquals(contact_type.name, 'mental message')
        self.assertEquals(contact_type.label_name, 'mental address id')

    def test_contact_type_unicode(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        self.assertEquals(contact_type.__unicode__(), contact_type.label_name)

    def test_create_contact(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        contact1 = Contact.objects.create(contact_type= contact_type, value = 'contact point', person= self.person, owner=self.user)
        self.assertTrue(contact1)
        self.assertFalse(contact1.is_bounced)
        self.assertEquals(contact1.contact_type, contact_type)
        self.assertEquals(contact1.value, 'contact point')
        self.assertEquals(contact1.person, self.person)

    def test_contact_unicode(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        contact1 = Contact.objects.create(contact_type= contact_type, value = 'contact point', person= self.person, owner=self.user)
        expected_unicode = _('%(contact)s (%(type)s)') % {
            'contact':contact1.value,
            'type':contact_type.label_name
        }

        self.assertEquals(contact1.__unicode__(), expected_unicode)

    def test_contact_has_owner(self):
        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        user = User.objects.all()[0]
        contact1 = Contact.objects.create(contact_type= contact_type, value = 'contact point', person= self.person, owner= user)
        
        self.assertEquals(contact1.owner, user)


    def test_when_a_contact_is_set_to_bounced_it_sends_a_mail_to_its_owner(self):
        #yeah I know that i kind of like to write big test names

        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        contact1 = Contact.objects.create(contact_type= contact_type, value = 'contact point', person= self.person, owner=self.user)

        contact1.is_bounced = True
        contact1.save()
        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact
        self.assertTrue(contact1.value in mail.outbox[0].body)
        self.assertTrue(self.person.name in mail.outbox[0].body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(self.user.email in mail.outbox[0].to)
        self.assertEquals(mail.outbox[0].subject, _('The contact contact point for Pedro has bounced'))
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_sends_a_notification_mail_only_once(self):

        contact_type = ContactType.objects.create(name='mental message', label_name = 'mental address id')
        contact1 = Contact.objects.create(contact_type= contact_type, value = 'contact point', person= self.person, owner=self.user)
        contact1.is_bounced = True
        contact1.save()
        contact1.save()

        self.assertEquals(len(mail.outbox), 1) #it is sent to one person pointed in the contact

        #@skip("it must first set the outbound_message to error")
    def test_it_sets_the_outbound_message_to_ready(self):
        contact = Contact.objects.get(id=1)#pedro
        contact.set_outbound_messages_to_ready()

        outbound_message = OutboundMessage.objects.get(contact=contact)
        self.assertEquals(outbound_message.status, 'ready')