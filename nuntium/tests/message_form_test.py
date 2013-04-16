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
        self.person1 = Person.objects.create(api_instance=self.api_instance1, name= 'Person 1')
        self.contact_type1 = ContactType.objects.create(name= 'e-mail',label_name='Electronic Mail')
        self.contact1 = Contact.objects.create(person=self.person1, contact_type=self.contact_type1, value= 'test@test.com')
        self.instance1 = Instance.objects.create(name='instance 1', slug= 'instance-1', api_instance= self.api_instance1)

    def test_create_form(self):
        #spanish
        data = {
        'subject':u'Fiera no está',
        'content':u'¿Dónde está Fiera Feroz? en la playa?',
        'instance': self.instance1.id,
        'contacts': [self.contact1.id]
        }


        form = MessageCreateForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())


    def test_instance_is_always_required(self):
        self.assertRaises(ValidationError, MessageCreateForm)
        form = MessageCreateForm(instance = self.instance1)
        self.assertTrue(form)
