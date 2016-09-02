from global_test_case import GlobalTestCase as TestCase
from nuntium.user_section.tests.user_section_views_tests import UserSectionTestCase
from contactos.models import ContactType, Contact
from popolo.models import Person
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core import mail
from django.conf import settings
from nuntium.models import OutboundMessage, Message, OutboundMessageIdentifier
from mailit.bin.handleemail import EmailHandler
from mailit.management.commands.handleemail import AnswerForManageCommand
from ..forms import ContactUpdateForm, ContactCreateForm
from django.test.client import RequestFactory, Client
from django.forms import ModelForm
from subdomains.utils import reverse
import simplejson as json
from instance.models import WriteItInstance
from django.db.models import Q
from django.contrib.sites.models import Site


class ContactTestCase(TestCase):
    def setUp(self):
        super(ContactTestCase, self).setUp()
        self.person = Person.objects.get(id=1)
        self.user = User.objects.get(id=1)

    def test_are_there_contacts_for_a_person_when_non_empty(self):
        felipe = Person.objects.get(name="Felipe")

        result = Contact.are_there_contacts_for(felipe)
        self.assertTrue(result)

    def test_are_there_contacts_for_a_person_when_empty(self):
        felipe = Person.objects.get(name="Felipe")
        felipe.contact_set.all().delete()

        result = Contact.are_there_contacts_for(felipe)
        self.assertFalse(result)

    def test_are_there_contacts_for_a_person_when_bounced(self):
        felipe = Person.objects.get(name="Felipe")
        for contact in felipe.contact_set.all():
            contact.is_bounced = True
            contact.save()

        result = Contact.are_there_contacts_for(felipe)
        self.assertFalse(result)

    def test_create_contact_type(self):
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        self.assertTrue(contact_type)
        self.assertEquals(contact_type.name, 'mental message')
        self.assertEquals(contact_type.label_name, 'mental address id')

    def test_contact_type_unicode(self):
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        self.assertEquals(contact_type.__unicode__(), contact_type.label_name)

    def test_create_contact(self):
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )
        self.assertTrue(contact1)
        self.assertFalse(contact1.is_bounced)
        self.assertEquals(contact1.contact_type, contact_type)
        self.assertEquals(contact1.value, 'contact point')
        self.assertEquals(contact1.person, self.person)
        self.assertTrue(contact1.enabled)

    def test_contact_with_writeitinstance(self):
        '''A contact is related to a writeit instance'''
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )
        self.assertTrue(contact1)
        self.assertFalse(contact1.is_bounced)
        self.assertEquals(contact1.contact_type, contact_type)
        self.assertEquals(contact1.value, 'contact point')
        self.assertEquals(contact1.person, self.person)
        self.assertEquals(contact1.writeitinstance, writeitinstance)

    def test_contacts_reverse_name(self):
        # Yeah I did another test just to say that I have one more
        # I don't see anything wrong with that
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )

        self.assertIn(contact1, writeitinstance.contacts.all())

    def test_contact_unicode(self):
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )
        expected_unicode = _('%(contact)s (%(type)s) for %(person)s') % {
            'contact': contact1.value,
            'type': contact_type.label_name,
            'person': self.person.name,
        }

        self.assertEquals(contact1.__unicode__(), expected_unicode)

    #I'm wondering if this test can be removed?
    def test_contact_has_owner(self):
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )

        self.assertEquals(contact1.writeitinstance, writeitinstance)

    def test_when_a_contact_is_set_to_bounced_it_sends_a_mail_to_its_owner(self):
        # yeah I know that i kind of like to write big test names
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact_type = ContactType.objects.create(
            name='mental message',
            label_name='mental address id',
            )
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )

        contact1.is_bounced = True
        contact1.save()
        self.assertEquals(len(mail.outbox), 1)  # it is sent to one person pointed in the contact
        self.assertTrue(contact1.value in mail.outbox[0].body)
        self.assertTrue(self.person.name in mail.outbox[0].body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(writeitinstance.owner.email in mail.outbox[0].to)
        self.assertEquals(mail.outbox[0].subject, _('The contact contact point for Pedro has bounced'))
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_sends_a_notification_mail_only_once(self):
        writeitinstance = WriteItInstance.objects.get(id=1)
        contact_type = ContactType.objects.create(
            name='mental message', label_name='mental address id')
        contact1 = Contact.objects.create(
            contact_type=contact_type,
            value='contact point',
            person=self.person,
            writeitinstance=writeitinstance,
            )
        contact1.is_bounced = True
        contact1.save()
        contact1.save()

        self.assertEquals(len(mail.outbox), 1)  # it is sent to one person pointed in the contact

        #@skip("it must first set the outbound_message to error")
    def test_it_sets_the_outbound_message_to_ready(self):
        contact = Contact.objects.get(id=1)  # pedro
        contact.set_outbound_messages_to_ready()

        outbound_messages = OutboundMessage.objects.filter(contact=contact)
        # I'm not entirely sure if this form of testing is correct
        # but what the f**k?
        for outbound_message in outbound_messages:
            self.assertEquals(outbound_message.status, 'ready')


class ResendOutboundMessages(TestCase):
    def setUp(self):
        super(ResendOutboundMessages, self).setUp()

        self.contact = Contact.objects.get(value="mailnoexistente@ciudadanointeligente.org")
        self.contact.is_bounced = True
        self.contact.save()
        self.outbound_messages = OutboundMessage.objects.filter(contact=self.contact)
        for outbound_message in self.outbound_messages:
            outbound_message.send()
            outbound_message.status = "error"
            outbound_message.save()
            identifier = OutboundMessageIdentifier.objects.get(outbound_message=outbound_message)
            identifier.key = "4aaaabbb"
            #This might fail if there are more than one outbound message!!!
            identifier.save()
            #This might fail if there are more than one outbound message!!
            #please fix if necesary by only choosing the first one or by using a try - except

        self.previous_amount_of_mails = len(mail.outbox)

        self.bounced_email = ""
        with open('mailit/tests/fixture/bounced_mail.txt') as f:
            self.bounced_email += f.read()
        f.close()
        self.handler = EmailHandler(answer_class=AnswerForManageCommand)
        self.answer = self.handler.handle(self.bounced_email)
        self.answer.send_back()

    def test_resend_outbound_messages(self):
        self.contact.resend_messages()

        outbound_messages = OutboundMessage.objects.filter(contact=self.contact)
        current_amount_of_mails_sent_after_resend_messages = len(mail.outbox)
        self.assertEquals(current_amount_of_mails_sent_after_resend_messages - self.previous_amount_of_mails, outbound_messages.count())
        for outbound_message in outbound_messages:
            self.assertEquals(outbound_message.status, "sent")

    def test_resends_only_failed_outbound_messages(self):
        message = Message.objects.get(id=1)
        OutboundMessage.objects.create(message=message, contact=self.contact, status="ready", site=Site.objects.get_current())
        self.contact.resend_messages()
        current_amount_of_mails_sent_after_resend_messages = len(mail.outbox)
        self.assertEquals(current_amount_of_mails_sent_after_resend_messages - self.previous_amount_of_mails,
        self.outbound_messages.count())

    def test_it_sets_the_is_bounced_status_to_false_of_the_contact(self):
        self.contact.resend_messages()

        contact = Contact.objects.get(id=self.contact.id)

        self.assertFalse(contact.is_bounced)


# Loving long names <3
class ContactCreateFormAndViewTestCase(UserSectionTestCase):
    def setUp(self):
        super(ContactCreateFormAndViewTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.get(id=1)
        self.writeitinstance = self.user.writeitinstances.get(id=2)
        # the password is already 'fiera' but I'm making this just
        # explicit
        self.user.set_password('fiera')
        self.user.save()
        # making it explicit
        self.contact_type = ContactType.objects.get(id=1)
        self.pedro = Person.objects.get(name="Pedro")

    def test_get_create_form(self):
        '''Get the form to display'''
        url = reverse('create-new-contact', kwargs={'pk': self.writeitinstance.pk, 'person_pk': self.pedro.id})
        self.assertTrue(url)
        c = Client()
        c.login(username=self.user.username, password="fiera")
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/profiles/contacts/create_new_contact_form.html')

    def test_create_a_new_contact_form(self):
        data = {
            'value': 'mail@the-real-mail.com'
        }
        form = ContactCreateForm(data=data, writeitinstance=self.writeitinstance, person=self.pedro)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEquals(self.writeitinstance.contacts.count(), 1)
        contact = self.writeitinstance.contacts.all()[0]
        self.assertEquals(contact.contact_type, self.contact_type)
        self.assertEquals(contact.value, data['value'])

    def test_can_create_a_new_contact_from_a_view(self):
        url = reverse('create-new-contact', kwargs={'pk': self.writeitinstance.pk, 'person_pk': self.pedro.id})
        self.assertTrue(url)

        c = Client()
        c.login(username=self.user.username, password="fiera")

        data = {
            'value': 'mail@the-real-mail.com'
        }

        response = c.post(url, data=data)
        self.assertEquals(response.status_code, 302)
        url_for_list_of_contacts = reverse('contacts-per-writeitinstance', subdomain=self.writeitinstance.slug)
        self.assertRedirects(response, url_for_list_of_contacts)

        contact = Contact.objects.get(Q(writeitinstance__owner=self.user), Q(value='mail@the-real-mail.com'))
        self.assertEquals(contact.value, data['value'])
        self.assertEquals(contact.person, self.pedro)
        self.assertEquals(contact.contact_type, self.contact_type)

    def test_select_widget_contains_api_instance(self):
        form = ContactCreateForm(writeitinstance=self.writeitinstance, person=self.pedro)
        self.assertTrue(form)
        self.assertIn('value', form.fields)
        self.assertEquals(len(form.fields), 1)


class ContactUpdateFormAndViewTestCase(UserSectionTestCase):
    def setUp(self):
        super(ContactUpdateFormAndViewTestCase, self).setUp()
        self.factory = RequestFactory()
        self.user = User.objects.get(username="fiera")
        self.writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.user)
        # the password is already fiera but I'm making this just
        # explicit
        self.user.set_password('fiera')
        # making it explicit

        self.contact = Contact.objects.get(id=1)
        self.contact.writeitinstance = self.writeitinstance
        self.contact.save()

    def test_create_form(self):
        form = ContactUpdateForm()
        self.assertIsInstance(form, ModelForm)
        self.assertEquals(form.Meta.model, Contact)
        self.assertEquals(form.Meta.fields, ['value'])

    def test_get_contact_value_update_view_not_allowed(self):
        url = reverse('contact_value_update', kwargs={'pk': self.contact.pk})

        c = Client()
        c.login(username='fiera', password="feroz")
        response = c.get(url)
        self.assertEquals(response.status_code, 405)

    def test_get_update_contact(self):
        url = reverse('contact_value_update', kwargs={'pk': self.contact.pk})

        c = Client()
        c.login(username='fiera', password="feroz")

        data = {'value': 'thenewvalue@value.com'}

        response = c.post(url, data=data)
        self.assertEquals(response.status_code, 200)

        contact = Contact.objects.get(id=self.contact.id)

        self.assertEquals(contact.value, data['value'])

        self.assertEquals(response['Content-Type'], 'application/json')
        json_answer = json.loads(response.content)
        self.assertEquals(json_answer['contact']['value'], data['value'])

    def test_get_update_contact_bounced_status(self):
        url = reverse('contact_value_update', kwargs={'pk': self.contact.pk})
        self.contact.is_bounced = True
        self.contact.save()

        c = Client()
        c.login(username='fiera', password="feroz")

        data = {'value': 'thenewvalue@value.com'}

        c.post(url, data=data)

        contact = Contact.objects.get(id=self.contact.id)

        self.assertFalse(contact.is_bounced)

    def test_a_non_login_cannot_update(self):
        url = reverse('contact_value_update', kwargs={'pk': self.contact.pk})
        #not_the_owner = User.objects.create_user(username="not_owner", password="123456")
        c = Client()
        #c.login(username='not_owner', password='123456')
        data = {'value': 'thenewvalue@value.com'}

        response = c.post(url, data=data)

        self.assertRedirectToLogin(response)

    def test_a_non_owner_cannot_update_a_contact(self):
        url = reverse('contact_value_update', kwargs={'pk': self.contact.pk})
        User.objects.create_user(username="not_owner", password="123456")
        c = Client()
        c.login(username='not_owner', password='123456')
        data = {'value': 'thenewvalue@value.com'}

        response = c.post(url, data=data)

        self.assertEquals(response.status_code, 404)
