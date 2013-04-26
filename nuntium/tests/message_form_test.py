# coding=utf-8
from django.test import TestCase
from popit.models import Person, ApiInstance
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage
from nuntium.forms import MessageCreateForm, PersonMultipleChoiceField
from django.forms import ValidationError,CheckboxSelectMultiple

class PersonMultipleChoiceFieldTestCase(TestCase):
    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance2, name= 'Person 2')

    def test_get_widget(self):
        field = PersonMultipleChoiceField(queryset=Person.objects.none())
        widget = field.widget

        self.assertTrue(isinstance(widget, CheckboxSelectMultiple))

    def test_get_label_from_instance(self):
        field = PersonMultipleChoiceField(queryset=Person.objects.all())
        label = field.label_from_instance(self.person1)

        self.assertEquals(label, self.person1.name)

class MessageFormTestCase(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance2, name= 'Person 2')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact2 = Contact.objects.create(person=self.person2, contact_type=self.contact_type1, value= 'test@test.com')
        self.writeitinstance1 = WriteItInstance.objects.create(name='instance 1', slug= 'instance-1', api_instance= self.api_instance1)
        self.writeitinstance2 = WriteItInstance.objects.create(name='instance 2', slug= 'instance-2', api_instance= self.api_instance2)

    def test_create_form(self):
        #spanish
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'persons': [self.person1.id]
        }


        form = MessageCreateForm(data, writeitinstance = self.writeitinstance1)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())


    def test_person_multiple_choice_field(self):
        form = MessageCreateForm(writeitinstance = self.writeitinstance1)
        persons_field = form.fields['persons']

        self.assertTrue(isinstance(persons_field, PersonMultipleChoiceField))


    def test_instance_is_always_required(self):
        self.assertRaises(ValidationError, MessageCreateForm)
        form = MessageCreateForm(writeitinstance = self.writeitinstance1)
        self.assertTrue(form)

    def test_form_only_has_contacts_from_its_instance(self):
        form = MessageCreateForm(writeitinstance = self.writeitinstance1)
        persons = form.fields['persons'].queryset
        self.assertEquals(len(persons), 1) #person 1 only
        self.assertEquals(persons[0], self.person1) #person 1

    def test_message_creation_on_form_save(self):
        #spanish
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'persons': [self.person1.id]
        }
        form = MessageCreateForm(data, writeitinstance=self.writeitinstance1)
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        new_messages = Message.objects.all()
        new_outbound_messages= OutboundMessage.objects.all()
        self.assertTrue(new_messages.count()>0)
        self.assertEquals(new_messages[0].subject, data['subject'])
        self.assertEquals(new_messages[0].content, data['content'])
        self.assertEquals(new_messages[0].writeitinstance, self.writeitinstance1)
        self.assertEquals(new_outbound_messages.count(),1)
        self.assertEquals(new_outbound_messages[0].contact, self.contact1)
        self.assertEquals(new_outbound_messages[0].message, new_messages[0])


    #there should be a test to prove that it does something when like sending 
    #a mental message or save it for later when we save the message
    #we save it
