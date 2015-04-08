# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from nuntium.models import WriteItInstance, Message
from subdomains.utils import reverse
from popit.models import Person
from nuntium.forms import WhoForm, DraftForm


class MessageCreationTestCase(TestCase):
    def setUp(self):
        super(MessageCreationTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.person1 = Person.objects.get(id=1)
        self.person2 = Person.objects.get(id=2)
        self.writeitinstance.add_person(self.person1)
        self.writeitinstance.add_person(self.person2)

    def test_go_through_the_whole_message_creation_process(self):
        '''Go through the whole message creation'''
        self.assertTrue(self.person1.contact_set.all())
        self.person2.contact_set.all().delete()

        url = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'who'})

        response = self.client.get(url)
        who_form = response.context['form']
        self.assertIsInstance(who_form, WhoForm)
        self.assertIn(self.person1, who_form.fields['persons'].queryset)
        # I'm expecting someone without contacts not to be in the
        # 'who' step.
        self.assertNotIn(self.person2, who_form.fields['persons'].queryset)

        self.assertIn('writeitinstance', response.context)
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance)
        recipient1 = self.writeitinstance.persons.get(id=1)
        response = self.client.post(url, data={
            'who-persons': [recipient1.id],
            'write_message_view-current_step': 'who'
            })
        url2 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'draft'})

        self.assertRedirects(response, url2)

        response = self.client.get(url2)
        self.assertIsInstance(response.context['form'], DraftForm)
        response = self.client.post(url2, data={
            'draft-subject': 'This is the subjectand is very specific',
            'draft-content': "This is the content",
            'draft-author_name': "Feli",
            'draft-author_email': 'email@mail.com',
            'write_message_view-current_step': 'draft'
            })

        url3 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'preview'})

        self.assertRedirects(response, url3)
        response = self.client.get(url3)
        self.assertEquals(response.context['message']['persons'][0].id, self.person1.id)
        # in this step I'm going to replicate the content of
        # response.context['message']['persons']
        # and
        # response.context['message']['people']
        # so we can use them in the template
        message_dict = response.context['message']
        self.assertEquals(message_dict['persons'], message_dict['people'])
        response = self.client.post(url3, data={
            'write_message_view-current_step': 'preview'
            })
        url4 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'done'})
        self.assertRedirects(response, url4)
        response = self.client.get(url4)
        url5 = reverse('write_message_sign', subdomain=self.writeitinstance.slug)
        self.assertEquals(response.url, url5)
        self.assertRedirects(response, url5)

        the_message = Message.objects.get(subject="This is the subjectand is very specific")
        self.assertTrue(the_message)
