# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from instance.models import PopoloPerson, WriteItInstance
from nuntium.models import Message
from subdomains.utils import reverse
from nuntium.forms import WhoForm, DraftForm


class MessageCreationTestCase(TestCase):
    def setUp(self):
        super(MessageCreationTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.person1 = PopoloPerson.objects.get(id=1)
        self.person2 = PopoloPerson.objects.get(id=2)
        self.writeitinstance.add_person(self.person1)
        self.writeitinstance.add_person(self.person2)

    def test_go_straight_to_draft_given_person_id(self):
        url = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'who'})
        url2 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'draft'})

        person_id = self.person1.identifiers.get(scheme='popolo:person').identifier

        response = self.client.get(url, {'person_id': person_id})
        self.assertRedirects(response, url2)
        response = self.client.get(url2)
        self.assertEquals(response.context['message']['persons'][0].id, self.person1.id)

    def test_if_theres_a_single_contact_skip_the_first_step(self):
        '''If theres a single contact skip the first step and select the single person'''
        url = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'who'})
        # Deleting Marcel
        self.writeitinstance.persons.get(id=2).delete()
        # ok so I've deleted Marcel from the list of people that is in this instance
        # so when I get this response I'm expecting to take me directly to
        # the second step .
        response = self.client.get(url)
        url2 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'draft'})

        self.assertRedirects(response, url2)
        response2 = self.client.get(url2)
        self.assertEquals(response2.status_code, 200)

    def test_go_through_the_whole_message_creation_process(self):
        '''Go through the whole message creation'''
        self.assertTrue(self.person1.contact_set.all())

        url = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'who'})

        response = self.client.get(url)
        who_form = response.context['form']
        self.assertIsInstance(who_form, WhoForm)
        self.assertIn(self.person1, who_form.fields['persons'].queryset)
        # I'm expecting someone without contacts not to be in the
        # 'who' step.
        self.assertIn('writeitinstance', response.context)
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance)
        recipient1 = self.writeitinstance.persons.get(id=1)
        response = self.client.post(url, data={
            'who_instance1-persons': [recipient1.id],
            'write_message_view-current_step': 'who'
            })
        url2 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'draft'})

        self.assertRedirects(response, url2)

        response = self.client.get(url2)
        self.assertIsInstance(response.context['form'], DraftForm)
        response = self.client.post(url2, data={
            'draft_instance1-subject': 'This is the subjectand is very specific',
            'draft_instance1-content': "This is the content",
            'draft_instance1-author_name': "Feli",
            'draft_instance1-author_email': 'email@mail.com',
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

    def test_passing_non_valid_forms_across_instances(self):
        '''Described at #715'''
        first_instance = WriteItInstance.objects.first()
        first_recipient = PopoloPerson.objects.get(id=2)

        second_instance = WriteItInstance.objects.last()

        url_who_first_instance = reverse('write_message_step',
            subdomain=first_instance.slug,
            kwargs={'step': 'who'})

        url_who_second_instance = reverse('write_message_step',
            subdomain=second_instance.slug,
            kwargs={'step': 'who'})

        self.client.post(url_who_first_instance, subdomain=first_instance.slug, data={
            'who_instance_1-persons': [first_recipient.id],
            'write_message_view-current_step': 'who'
            })

        response_get_to_draft_second_instance = self.client.get(url_who_second_instance, subdomain=second_instance.slug)
        who_form_for_second_instance = response_get_to_draft_second_instance.context['form']
        self.assertFalse(who_form_for_second_instance.errors)

    def test_message_creation_with_anonymous_author_process(self):
        '''check we can have anonymous authors'''
        self.assertTrue(self.person1.contact_set.all())
        self.writeitinstance.config.allow_anonymous_messages = True
        self.writeitinstance.config.save()

        url = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'who'})

        response = self.client.get(url)
        who_form = response.context['form']
        self.assertIsInstance(who_form, WhoForm)
        self.assertIn(self.person1, who_form.fields['persons'].queryset)
        # I'm expecting someone without contacts not to be in the
        # 'who' step.
        self.assertIn('writeitinstance', response.context)
        self.assertEquals(response.context['writeitinstance'], self.writeitinstance)
        recipient1 = self.writeitinstance.persons.get(id=1)
        response = self.client.post(url, data={
            'who_instance1-persons': [recipient1.id],
            'write_message_view-current_step': 'who'
            })
        url2 = reverse('write_message_step',
            subdomain=self.writeitinstance.slug,
            kwargs={'step': 'draft'})

        self.assertRedirects(response, url2)

        response = self.client.get(url2)
        self.assertIsInstance(response.context['form'], DraftForm)
        response = self.client.post(url2, data={
            'draft_instance1-subject': 'This is the subjectand is very specific',
            'draft_instance1-content': "This is the content",
            'draft_instance1-author_email': 'email@mail.com',
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
