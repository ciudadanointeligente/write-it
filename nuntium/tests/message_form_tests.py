# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from contactos.models import Contact, ContactType
from instance.models import InstanceMembership, PopoloPerson, WriteItInstance
from popolo_sources.models import PopoloSource
from ..models import Message, Confirmation, OutboundMessage
from ..forms import MessageCreateForm, PersonMultipleChoiceField

from django.forms import ValidationError, SelectMultiple
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class PersonMultipleChoiceFieldTestCase(TestCase):
    def setUp(self):
        super(PersonMultipleChoiceFieldTestCase, self).setUp()
        self.person1 = PopoloPerson.objects.get(id=1)

    def test_get_widget(self):
        field = PersonMultipleChoiceField(queryset=PopoloPerson.objects.none())
        widget = field.widget

        self.assertTrue(isinstance(widget, SelectMultiple))

    def test_get_label_from_instance(self):
        field = PersonMultipleChoiceField(
            queryset=PopoloPerson.objects.prefetch_related('contact_set'))
        label = field.label_from_instance(self.person1)

        self.assertEquals(label, self.person1.name)

    def test_persons_without_a_contact(self):
        felipe = PopoloPerson.objects.get(name="Felipe")
        felipe.contact_set.all().delete()
        # This guy does not have any contacts
        field = PersonMultipleChoiceField(
            queryset=PopoloPerson.objects.prefetch_related('contact_set'))
        rendered_field = field.widget.render(name='oli', value=None)
        self.assertIn('class="uncontactable"', rendered_field)
        self.assertIn(">Felipe</option>", rendered_field)

    def test_persons_with_bounced_contact(self):
        felipe = PopoloPerson.objects.get(name="Felipe")
        for contact in felipe.contact_set.all():
            contact.is_bounced = True
            contact.save()

        # This guy does not have any good contacts
        field = PersonMultipleChoiceField(
            queryset=PopoloPerson.objects.prefetch_related('contact_set'))
        rendered_field = field.widget.render(name='oli', value=None)
        self.assertIn('class="uncontactable"', rendered_field)
        self.assertIn(">Felipe</option>", rendered_field)

    def test_persons_with_bounced_contact_unicode(self):
        felipe = PopoloPerson.objects.get(name="Felipe")
        felipe.name = u"Felipe Álvarez"
        felipe.save()

        for contact in felipe.contact_set.all():
            contact.is_bounced = True
            contact.save()

        # This guy does not have any good contacts
        field = PersonMultipleChoiceField(
            queryset=PopoloPerson.objects.prefetch_related('contact_set'))
        rendered_field = field.widget.render(name='oli', value=None)
        self.assertIn('class="uncontactable"', rendered_field)
        self.assertIn(u">Felipe Álvarez</option>", rendered_field)

    def test_previously_selected_persons(self):
        field = PersonMultipleChoiceField(
            queryset=PopoloPerson.objects.prefetch_related('contact_set'))
        rendered_field = field.widget.render(name='oli', value=[3])
        self.assertIn('<option class="" value="3" selected="selected">Felipe</option>', rendered_field)

    def test_not_too_many_queries(self):
        wii = WriteItInstance.objects.get(id=1)
        email_type = ContactType.objects.get(id=1)
        popolo_source = PopoloSource.objects.get(pk=1)
        for name, email in [
                ('Alice', 'alice@example.com'),
                ('Bob', 'bob@example.com'),
                ('Charles', 'charles@example.com'),
                ('Mallory', 'mallory@example.com'),
        ]:
            p = PopoloPerson.objects.create(name=name)
            p.add_link_to_popolo_source(popolo_source)
            Contact.objects.create(
                person=p,
                contact_type=email_type,
                writeitinstance=wii,
                value=email)
        # Ideally, this should just be two queries - one for the query
        # on Person and one of the prefetch on Contact; however, the
        # querset actually gets evaluated twice at the moment: once in
        # the initializer of PersonSelectMultipleWidget and once when
        # render_options evaluates 'choices'.  So this isn't ideal,
        # but this assertion at least should catch anyone changing the
        # code back so that there's the N+1 queries problem. As of
        # Django 1.8, there appear to also be 4 queries that create
        # and release savepoints.
        with self.assertNumQueries(8):
            field = PersonMultipleChoiceField(
                queryset=Person.objects.prefetch_related('contact_set'))
            rendered_field = field.widget.render(name='oli', value=None)
            self.assertNotIn('uncontactable', rendered_field)

class MessageFormTestCase(TestCase):
    def setUp(self):
        super(MessageFormTestCase, self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.person1 = PopoloPerson.objects.get(id=1)
        self.contact1 = Contact.objects.get(id=1)

    def test_form_fields(self):
        form = MessageCreateForm(writeitinstance=self.writeitinstance1)
        self.assertTrue("persons" in form.fields)
        self.assertTrue("subject" in form.fields)
        self.assertTrue("content" in form.fields)
        self.assertTrue("author_name" in form.fields)
        self.assertTrue("author_email" in form.fields)
        self.assertTrue("slug" not in form.fields)
        self.assertNotIn('moderated', form.fields)
        self.assertNotIn('confirmated', form.fields)

    def test_create_form(self):
        # Spanish
        data = {
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name': u"Felipe",
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id],
            }

        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())

    def test_when_an_instance_does_not_allow_new_messages_throu_the_form_it_does_not_validate(self):
        # Spanish
        data = {
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name': u"Felipe",
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id],
            }
        self.writeitinstance1.config.allow_messages_using_form = False
        self.writeitinstance1.config.save()

        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)
        self.assertTrue(form)
        self.assertFalse(form.is_valid())

    def test_person_multiple_choice_field(self):
        form = MessageCreateForm(writeitinstance=self.writeitinstance1)
        persons_field = form.fields['persons']

        self.assertTrue(isinstance(persons_field, PersonMultipleChoiceField))

    def test_instance_is_always_required(self):
        self.assertRaises(ValidationError, MessageCreateForm)
        form = MessageCreateForm(writeitinstance=self.writeitinstance1)
        self.assertTrue(form)

    def test_form_only_has_contacts_from_its_instance(self):
        form = MessageCreateForm(writeitinstance=self.writeitinstance1)
        persons = form.fields['persons'].queryset
        self.assertEquals(len(persons), 1)  # person 1 only
        self.assertEquals(persons[0], self.person1)  # person 1

    def test_message_creation_on_form_save(self):
        # Spanish
        data = {
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name': u"Felipe",
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id],
            }
        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        new_message = Message.objects.get(subject=data['subject'], content=data['content'])

        new_outbound_messages = OutboundMessage.objects.filter(message=new_message)
        self.assertEquals(new_message.subject, data['subject'])
        self.assertEquals(new_message.content, data['content'])
        self.assertEquals(new_message.writeitinstance, self.writeitinstance1)
        self.assertEquals(new_outbound_messages.count(), 1)
        self.assertEquals(new_outbound_messages[0].contact, self.contact1)
        self.assertEquals(new_outbound_messages[0].message, new_message)
        self.assertEquals(new_outbound_messages[0].status, "new")

    def test_it_creates_a_confirmation(self):
        # Spanish
        data = {
            'subject': u'Amor a la fiera',
            'content': u'Todos sabemos que quieres mucho a la Fiera pero... es verdad?',
            'author_name': u"Felipe",
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id],
            }
        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        new_message = Message.objects.get(subject=data['subject'], content=data['content'])
        confirmation = Confirmation.objects.get(message=new_message)

        self.assertEquals(len(confirmation.key.strip()), 32)
        self.assertTrue(confirmation.confirmated_at is None)

    # there should be a test to prove that it does something when like sending
    # a mental message or save it for later when we save the message
    # we save it

    def test_maximum_recipients(self):
        '''When creating a message that includes more than maximum_recipients'''
        self.writeitinstance1.config.maximum_recipients = 1
        self.writeitinstance1.config.save()
        person2 = PopoloPerson.objects.get(id=2)
        InstanceMembership.objects.create(writeitinstance=self.writeitinstance1, person=person2)
        data = {
            'subject': u'Amor a la fiera',
            'content': u'Todos sabemos que quieres mucho a la Fiera pero... es verdad?',
            'author_name': u"Felipe",
            'author_email': u"falvarez@votainteligente.cl",
            'persons': [self.person1.id, person2.id],
            }
        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)
        form.full_clean()
        self.assertFalse(form.is_valid())

        self.assertTrue(form.errors)


class RateLimitingInForm(TestCase):
    def setUp(self):
        super(RateLimitingInForm, self).setUp()
        self.owner = User.objects.get(id=1)
        self.writeitinstance1 = WriteItInstance.objects.get(id=1)
        self.writeitinstance1.config.rate_limiter = 1
        self.writeitinstance1.config.save()
        self.person1 = PopoloPerson.objects.get(id=1)
        self.person2 = PopoloPerson.objects.get(id=2)
        self.message = Message.objects.get(id=1)
        Message.objects.create(
            content='Content 1',
            author_name='Felipe',
            author_email="fiera@votainteligente.cl",
            confirmated=True,
            subject='Test',
            writeitinstance=self.writeitinstance1,
            persons=[self.person1],
            )

    def test_clean_method_throws_error_when_rate_limit_is_reached(self):
        data = {
            'subject': u'Fiera no está',
            'content': u'¿Dónde está Fiera Feroz? en la playa?',
            'author_name': u"Felipe",
            'author_email': u"fiera@votainteligente.cl",
            'persons': [self.person1.id],
            }
        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)

        form.full_clean()
        self.assertFalse(form.errors is None)
        self.assertIn(_('You have reached your limit for today please try again tomorrow'), form.non_field_errors())
