# coding=utf-8
from global_test_case import GlobalTestCase as TestCase
from django.utils.unittest import skip
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from contactos.models import Contact, ContactType
from nuntium.models import Message, WriteItInstance, OutboundMessage, MessageRecord, Confirmation, Moderation
from popit.models import Person, ApiInstance
from subdomains.utils import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core import mail
from mock import patch
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
import datetime
from django.utils.translation import activate
from subdomains.tests import SubdomainTestMixin
from django.core.management import call_command


class TestMessages(TestCase):

    def setUp(self):
        super(TestMessages,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.person2 = Person.objects.all()[1]


    def test_create_message(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        self.assertTrue(message)
        self.assertEquals(message.content, "Content 1")
        self.assertEquals(message.subject, "Fiera es una perra feroz")
        self.assertEquals(message.writeitinstance, self.writeitinstance1)
        self.assertEquals(message.slug, slugify(message.subject))
        self.assertFalse(message.confirmated)
        self.assertTrue(message.public)

        self.assertTrue(message.moderated is None)


    def test_message_has_a_is_confirmated_field(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Fiera es una perra feroz', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        self.assertTrue(message.confirmated)

    #This intended to fix this bug
    #https://github.com/ciudadanointeligente/write-it/issues/167
    def test_two_messages_with_the_same_slug_throw_an_error(self):
        

        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='test',
            slug='test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        message2 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='test', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        message2.slug='test'
        with self.assertRaises(IntegrityError):
            message2.save()

    def test_two_messages_with_different_capital_letters(self):
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        message2 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='test', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        self.assertNotEqual(message1.slug, message2.slug)

    def test_a_message_with_a_changed_slug(self):
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        message1.slug = 'test-2'
        message1.save()

        regex = "^"+message1.slug+"(-\d+){0,1}$"
        previously = Message.objects.filter(slug__regex=regex).count()

        message2 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='test', 
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])


        self.assertEquals(message2.slug, 'test-3')

        
    def test_four_messaes_with_the_same_slug(self):
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        message2 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        message3 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])
        message4 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl",
            confirmated = True,
            subject='Test',
            writeitinstance= self.writeitinstance1,
            persons = [self.person1])

        self.assertEquals(message1.slug, 'test')
        self.assertEquals(message2.slug, 'test-2')
        self.assertEquals(message3.slug, 'test-3')
        self.assertEquals(message4.slug, 'test-4')


    def test_update_a_message_does_not_need_persons(self):
        message1 = Message.objects.all()[0]

        previous_people = message1.people

        message1.slug = 'a-new-slug1'

        message1.save()

        self.assertEquals(message1.people, previous_people)


    def test_message_has_a_permalink(self):
        message1 = Message.objects.all()[0]
        expected_url = reverse('message_detail',subdomain=message1.writeitinstance.slug, kwargs={'slug':message1.slug})

        self.assertEquals(expected_url, message1.get_absolute_url())


    def test_message_set_to_ready(self):
        message1 = Message.objects.all()[0]

        message1.set_to_ready()
        first_om = OutboundMessage.objects.filter(message=message1)[0]
        second_om = OutboundMessage.objects.filter(message=message1)[1]

        self.assertEquals(first_om.status, 'ready')
        self.assertEquals(second_om.status, 'ready')


    def test_two_messages_with_the_same_subject_but_different_slug(self):
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

        message2 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

        message3 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])


        self.assertEquals(message1.slug, slugify(message1.subject))
        self.assertEquals(message2.slug, slugify(message2.subject)+"-2")
        self.assertEquals(message3.slug, slugify(message3.subject)+"-3")


    def test_a_person_with_two_contacts_method_people(self):
        user = User.objects.all()[0]
        contact = Contact.objects.create(person=self.person1
            , value=u"another@contact.cl"
            , contact_type=self.person1.contact_set.all()[0].contact_type
            , owner=user)
        
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])


        self.assertEquals(message.people, [self.person1])


    def test_resave_a_message_should_not_change_slug(self):
        #There are a lot of good solutions for this problem but this
        #is the easyest one
        message1 = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        previous_slug = message1.slug
        #message1 now has a slug
        message1.subject = 'Some other subject and stuff'
        message1.save()

        self.assertEquals(message1.slug, previous_slug)


    def test_a_message_has_a_people_property(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Same subject hey', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1, self.person2])

        self.assertEquals(message.people, [self.person1, self.person2])


    def test_message_unicode(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])

        self.assertEquals(message.__unicode__(), _('%(subject)s at %(instance)s') % {
            'subject':message.subject,
            'instance':self.writeitinstance1.name
            })

    def test_outboundmessage_create_without_manager(self):
        message = Message(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        
        self.assertEquals(message.outboundmessage_set.count(), 1)

    def test_outbound_message_is_not_created_if_the_persons_contact_is_bounced(self):
        contact = Contact.objects.get(person=self.person1)
        contact.is_bounced = True
        contact.save()
        message = Message(content = 'Content 1', author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        message.save()

        self.assertEquals(message.outboundmessage_set.count(), 0)

    def test_outbound_message_is_not_created_if_the_contact_is_owned_by_some_other_user(self):
        #test names are big but I think that's the way to indicate my intention
        felipe = User.objects.create_user(username='felipe', password='lafieratienepulgas')
        contact = Contact.objects.create(person=self.person1
            , value=u"another@contact.cl"
            , contact_type=self.person1.contact_set.all()[0].contact_type
            , owner=felipe)

        #this contact is for person 1 but it is owned by felipe
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

        #there should not be any outboundmessages to contact because the message was
        #sent to writeitinstance1 that is owned by felipe



        self.assertEquals(OutboundMessage.objects.filter(contact=contact).count(), 0)


    def test_it_creates_outbound_messages_only_once(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])
        message.save()

        self.assertEquals(OutboundMessage.objects.filter(message=message).count(), 1)

    def test_it_raises_typeerror_when_no_contacts_are_present(self):
        with self.assertRaises(TypeError):
            Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1)

    def test_message_set_new_outbound_messages_to_ready(self):
        message = Message.objects.create(content = 'Content 1', author_name='Felipe', author_email="falvarez@votainteligente.cl", subject='Subject 1', writeitinstance= self.writeitinstance1, persons = [self.person1])

        message.recently_confirmated()

        outbound_message_to_pedro = OutboundMessage.objects.filter(message=message)[0]
        self.assertEquals(outbound_message_to_pedro.status, 'ready')
        self.assertTrue(message.confirmated)


class PublicMessagesManager(TestCase, SubdomainTestMixin):
    def setUp(self):
        super(PublicMessagesManager, self).setUp()
        self.moderation_not_needed_instance = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.moderable_instance = WriteItInstance.objects.all()[1]
        self.moderable_instance.moderation_needed_in_all_messages = True

        self.moderable_instance.save()

    def test_public_non_confirmated_message_is_not_in_the_public(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='public non confirmated message', 
            writeitinstance= self.moderation_not_needed_instance, 
            persons = [self.person1])
        Confirmation.objects.create(message=message)

        self.assertNotIn(message, Message.objects.public())

        message.recently_confirmated()

        self.assertIn(message, Message.objects.public())

    def test_confirmated_but_non_moderated_message_in_a_moderable_instance_is_not_shown(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='public non confirmated message', 
            writeitinstance= self.moderable_instance, 
            persons = [self.person1])

        Confirmation.objects.create(message=message)
        self.assertNotIn(message, Message.objects.public())
        message.recently_confirmated()

        #the important one
        self.assertNotIn(message, Message.objects.public())










class MessageDetailView(TestCase, SubdomainTestMixin):
    def setUp(self):
        super(MessageDetailView,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        Confirmation.objects.create(message=self.message, confirmated_at = datetime.datetime.now())


    def test_get_message_detail_page(self):
        #I'm kind of feeling like I need 
        #something like rspec or cucumber
        host = self.get_host_for_subdomain(self.message.writeitinstance.slug)
        url = self.message.get_absolute_url()
        self.assertTrue(url)

        response = self.client.get(url,HTTP_HOST=host)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], self.message)

    def test_get_message_detail_that_was_created_using_the_api(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            public=True,
            writeitinstance= self.writeitinstance1, 
            confirmated = True,
            persons = [self.person1])

        #this message is confirmated but has no confirmation object
        #this occurs when creating a message throu the API
        url = message.get_absolute_url()
        host = self.get_host_for_subdomain(self.message.writeitinstance.slug)
        response = self.client.get(url,HTTP_HOST=host)
        self.assertEquals(response.status_code, 200)


    def test_get_messages_without_confirmation_and_not_confirmed(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            public=False,
            writeitinstance= self.writeitinstance1, 
            confirmated = False,
            persons = [self.person1])

        #this message is confirmated but has no confirmation object
        #this occurs when creating a message throu the API
        host = self.get_host_for_subdomain(message.writeitinstance.slug)
        url = message.get_absolute_url()
        response = self.client.get(url,HTTP_HOST=host)
        self.assertEquals(response.status_code, 404)

        
class AllMessagesWithModerationInAWriteItInstances(TestCase):
    def setUp(self):
        super(AllMessagesWithModerationInAWriteItInstances,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.writeitinstance1.moderation_needed_in_all_messages = True
        self.writeitinstance1.save()
        self.person1 = Person.objects.all()[0]
        self.message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1',
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

    def test_a_message_is_considered_not_moderated(self):
        
        self.assertFalse(self.message.moderated is None)
        self.assertFalse(self.message.moderated)

    def test_a_message_moderated_status_is_changed(self):
        self.message.moderated = True
        self.message.save()

        message = Message.objects.get(id=self.message.id)

        self.assertTrue(message.moderated)

    def test_a_message_does_not_have_a_moderation_previous_to_confirmation(self):
        self.assertEquals(Moderation.objects.filter(message=self.message).count(), 0)

    def test_when_you_create_a_public_message_in_the_instance(self):
        self.assertEquals(len(mail.outbox),0)
        #the message is confirmated
        self.message.recently_confirmated()

        self.assertFalse(self.message.moderation is None)
        self.assertEquals(len(mail.outbox),1)
        #the second should be the confirmation thing
        #just to make sure 
        self.assertModerationMailSent(self.message, mail.outbox[0])


class ModerationMessagesTestCase(TestCase, SubdomainTestMixin):
    def setUp(self):
        super(ModerationMessagesTestCase,self).setUp()
        self.writeitinstance1 = WriteItInstance.objects.all()[0]
        self.person1 = Person.objects.all()[0]
        self.private_message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Subject 1', 
            public=False,
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])
        self.confirmation = Confirmation.objects.create(message=self.private_message)
        self.host = self.get_host_for_subdomain(self.writeitinstance1.slug)

    def test_private_messages_confirmation_created_move_from_new_to_needs_moderation(self):
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.recently_confirmated()
        
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message)
        self.assertEquals(outbound_message_to_pedro.status, 'needmodera')


    def test_private_message_is_not_accesible(self):
        self.confirmation.confirmated_at = datetime.datetime.now()
        self.confirmation.save()
        self.private_message.confirmated = True
        self.private_message.save()
        host = self.get_host_for_subdomain(self.private_message.writeitinstance.slug)
        url = self.private_message.get_absolute_url()
        response = self.client.get(url,HTTP_HOST=host)

        self.assertEquals(response.status_code, 404)


    def test_outbound_messages_of_a_confirmed_message_are_waiting_for_moderation(self):
        #I need to do a get to the confirmation url
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        url = reverse('confirm', kwargs={
            'slug':self.confirmation.key
            })
        response = self.client.get(url)
        #this works proven somewhere else
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message)
        self.assertEquals(outbound_message_to_pedro.status, 'needmodera')

    def test_message_send_moderation_message(self):
        moderation, created = Moderation.objects.get_or_create(message=self.private_message)
        self.private_message.send_moderation_mail()

        self.assertEquals(len(mail.outbox),2)
        moderation_mail = mail.outbox[1]
        self.assertModerationMailSent(self.private_message, moderation_mail)
        
    def test_create_a_moderation(self):
        #I make sure that uuid.uuid1 is called and I get a sort of random key
        with patch('uuid.uuid1') as string:
            string.return_value.hex = 'oliwi'
            message = Message.objects.create(content = 'Content 1', 
                author_name='Felipe', 
                author_email="falvarez@votainteligente.cl", 
                subject='Fiera es una perra feroz', 
                public=False,
                writeitinstance= self.writeitinstance1, 
                persons = [self.person1])

            self.assertFalse(message.moderation is None)
            self.assertEquals(message.moderation.key, 'oliwi')
            string.assert_called()
    #issue 114 found at https://github.com/ciudadanointeligente/write-it/issues/114
    def test_send_mails_only_once(self):
        with patch('nuntium.models.Message.send_moderation_mail') as send_moderation_mail:
            self.writeitinstance1.moderation_needed_in_all_messages = True
            self.writeitinstance1.save()

            send_moderation_mail.return_value = None
            message = Message.objects.create(content = 'Content 1', 
                author_name='Felipe', 
                author_email="falvarez@votainteligente.cl", 
                subject='Fiera es una perra feroz', 
                public=False,
                writeitinstance= self.writeitinstance1, 
                persons = [self.person1])

            message.recently_confirmated()


            number_of_moderations = Moderation.objects.filter(message=message).count()
            send_moderation_mail.assert_called_once_with()

    def test_there_is_a_moderation_url_that_sets_the_message_to_ready(self):
        url = reverse('moderation_accept', kwargs={
            'slug': self.private_message.moderation.key
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/moderation_accepted.html')

        #private_message = Message.objects.get(id=self.private_message.id)
        outbound_message_to_pedro = OutboundMessage.objects.get(message=self.private_message.id)
        self.assertEquals(outbound_message_to_pedro.status, 'ready')
        private_message = Message.objects.get(id=self.private_message.id)
        self.assertTrue(private_message.moderated)

    def test_moderation_get_success_url(self):
        expected_url = reverse('moderation_accept', kwargs={
            'slug': self.private_message.moderation.key
            })
        self.assertEquals(self.private_message.moderation.get_success_url(), expected_url)

    def test_moderation_get_reject_url(self):
        expected_url = reverse('moderation_rejected', kwargs={
            'slug': self.private_message.moderation.key
            })
        self.assertEquals(self.private_message.moderation.get_reject_url(), expected_url)

    def test_there_is_a_reject_moderation_url_that_deletes_the_message(self):
        '''
        This is the case when you proud owner of a writeitInstance 
        think that the private message should not go anywhere
        and it should be deleted
        '''
        url = reverse('moderation_rejected', kwargs={
            'slug': self.private_message.moderation.key
            })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/moderation_rejected.html')
        #If someone knows how to do the DoesNotExist or where to extend from 
        #I could do a self.assertRaises but I'm not taking any more time in this
        self.assertEquals(Message.objects.filter(id=self.private_message.id).count(), 0)


    def test_when_moderation_needed_a_mail_for_its_owner_is_sent(self):
        self.private_message.recently_confirmated()
        #There should be two 
        #One is created for confirmation
        #The other one is created for the moderation thing
        self.assertEquals(len(mail.outbox),2)
        moderation_mail = mail.outbox[1]
        #it is sent to the owner of the instance
        self.assertEquals(moderation_mail.to[0], self.private_message.writeitinstance.owner.email)
        self.assertTrue(self.private_message.content in moderation_mail.body)
        self.assertTrue(self.private_message.subject in moderation_mail.body)
        self.assertTrue(self.private_message.author_name in moderation_mail.body)
        self.assertTrue(self.private_message.author_email in moderation_mail.body)
        current_site = Site.objects.get_current()
        current_domain = 'http://'+current_site.domain
        url_rejected = reverse('moderation_rejected', kwargs={
            'slug': self.private_message.moderation.key
            })

        url_accept = reverse('moderation_accept', kwargs={
            'slug': self.private_message.moderation.key
            })


        self.assertFalse(current_domain+url_rejected in moderation_mail.body)
        self.assertTrue(url_rejected in moderation_mail.body)
        self.assertFalse(current_domain+url_accept in moderation_mail.body)
        self.assertTrue(url_accept in moderation_mail.body)



    def test_creates_automatically_a_moderation_when_a_private_message_is_created(self):
        message = Message.objects.create(content = 'Content 1', 
            author_name='Felipe', 
            author_email="falvarez@votainteligente.cl", 
            subject='Fiera es una perra feroz', 
            public=False,
            writeitinstance= self.writeitinstance1, 
            persons = [self.person1])

        self.assertFalse(message.moderation is None)


    def test_a_moderation_does_not_change_its_key_on_save(self):
        '''
        I found that everytime I did resave a moderation
        it key was regenerated
        '''
        previous_key = self.private_message.moderation.key
        self.private_message.moderation.save()
        moderation = Moderation.objects.get(message=self.private_message)
        post_key = moderation.key

        self.assertEquals(previous_key, post_key)

    def test_moderates_method(self):
        moderation = Moderation.objects.get(message=self.private_message)
        moderation.success()

        message = Message.objects.get(moderation=moderation)
        self.assertTrue(message.moderated)


    #this test is for the issue https://github.com/ciudadanointeligente/write-it/issues/186
    #
    def test_confirmated_but_not_moderated_message_in_a_moderable_instance_is_in_needs_moderation_status(self):
        mail_count = len(mail.outbox)
        self.writeitinstance1.moderation_needed_in_all_messages = True
        self.writeitinstance1.save()

        data = {
            'author_email':u'falvarez@votainteligente.cl',
            'author_name':u'feli',
            'public':True,
            'subject':u'Fiera no está',
            'content':u'¿Dónde está Fiera Feroz? en la playa?',
            'persons': [self.person1.id]
        }
        url = self.writeitinstance1.get_absolute_url()
        response = self.client.post(url, data, follow=True, HTTP_HOST=self.host)
        message = Message.objects.get(
            author_name="feli", 
            author_email="falvarez@votainteligente.cl",
            subject="Fiera no está", 
            content='¿Dónde está Fiera Feroz? en la playa?')
        confirmation = Confirmation.objects.get(message=message)

        confirmation_response = self.client.get(confirmation.get_absolute_url())

        #one message to Pedro
        outbound_message = OutboundMessage.objects.get(message=message)
        #Here I have the bug!!!!!
        self.assertEquals(outbound_message.status, 'needmodera')
        #This one is the bug!!\

