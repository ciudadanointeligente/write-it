# coding=utf-8
from django.test import TestCase
from popit.models import Person, ApiInstance
from contactos.models import Contact, ContactType
from nuntium.models import Message, Instance, MessageOutbox
from nuntium.forms import MessageCreateForm
from django.forms import ValidationError


class MessageFormTestCase(TestCase):

    def setUp(self):
        self.api_instance1 = ApiInstance.objects.create(url='http://popit.org/api/v1')
        self.api_instance2 = ApiInstance.objects.create(url='http://popit.org/api/v2')
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.person2 = Person.objects.create(api_instance=self.api_instance2, name= 'Person 2')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.contact2 = Contact.objects.create(person=self.person2, contact_type=self.contact_type1, value= 'test@test.com')
        self.instance1 = Instance.objects.create(name='instance 1', slug= 'instance-1', api_instance= self.api_instance1)
        self.instance2 = Instance.objects.create(name='instance 2', slug= 'instance-2', api_instance= self.api_instance2)

    def test_create_form(self):
        #spanish
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'instance': self.instance1.id,
        'persons': [self.person1.id]
        }


        form = MessageCreateForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())


    def test_instance_is_always_required(self):
        self.assertRaises(ValidationError, MessageCreateForm)
        form = MessageCreateForm(instance = self.instance1)
        self.assertTrue(form)

    def test_the_form_only_has_its_contacts(self):
        form = MessageCreateForm(instance = self.instance1)
        persons = form.fields['persons'].queryset
        self.assertEquals(len(persons), 1) #person 1 only
        self.assertEquals(persons[0], self.person1) #person 1


    #there should be a test to prove that it does something when like sending 
    #a mental message or save it for later when we save the message
    #we save it
