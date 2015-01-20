from global_test_case import popit_load_data
from django.core.urlresolvers import reverse
from ...models import WriteItInstance, Membership, WriteitInstancePopitInstanceRecord
from django.contrib.auth.models import User
from django.test.client import Client
from django.forms import Form, URLField
from django.conf import settings
from django.core.management import call_command
from popit.models import Person, ApiInstance
from django.utils.unittest import skipUnless
from user_section_views_tests import UserSectionTestCase
from django.utils.translation import ugettext as _
from nuntium.user_section.forms import RelatePopitInstanceWithWriteItInstance


class UpdateMyPopitInstancesTestCase(UserSectionTestCase):
    def setUp(self):
        super(UpdateMyPopitInstancesTestCase, self).setUp()
        self.user = User.objects.create_user(username="fieraferoz", password="feroz")

    def test_a_url_is_reachable(self):
        '''My popit instances url is reachable'''
        url = reverse('my-popit-instances')
        self.assertTrue(url)

    def test_it_brings_all_the_popit_apis(self):
        '''My popit apis admin page brings all my popit apis'''
        benito = User.objects.create_user(username="benito", password="feroz")
        benitos_instance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=benito,
            )

        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.user,
            )

        instance1 = ApiInstance.objects.create(url="http://foo.com/api")
        instance2 = ApiInstance.objects.create(url="http://foo2.com/api")
        instance3 = ApiInstance.objects.create(url="http://foo3.com/api")

        fiera = Person.objects.create(api_instance=instance1, name="fiera")
        benito = Person.objects.create(api_instance=instance2, name="benito")
        Person.objects.create(api_instance=instance3, name="ac")

        Membership.objects.create(writeitinstance=writeitinstance, person=fiera)
        Membership.objects.create(writeitinstance=writeitinstance, person=benito)

        record1 = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=instance1,
            )
        record2 = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=instance2,
            )
        record3 = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=benitos_instance,
            popitapiinstance=instance3,
            )

        c = Client()

        c.login(username="fieraferoz", password="feroz")
        url = reverse('my-popit-instances')
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIn(record1, response.context['object_list'])
        self.assertIn(record2, response.context['object_list'])
        self.assertNotIn(record3, response.context['object_list'])

        self.assertTemplateUsed(response, 'nuntium/profiles/your-popit-apis.html')
        self.assertTemplateUsed(response, 'base_edit.html')

    def test_I_can_only_access_if_I_logged_in(self):
        ''' I can only access my popit apis if Im logged in'''
        c = Client()

        # the following line is commented on porpouse
        # c.login(username="fieraferoz", password="feroz")
        # to show that c is not logged in
        url = reverse('my-popit-instances')

        response = c.get(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_there_is_a_url_where_you_can_update_a_popit_instance(self):
        '''There is a url to update a popit instance'''
        api_instance = ApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.user,
            )

        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=api_instance,
            )
        url = reverse('rerelate-writeit-popit', kwargs={'pk': record.pk})
        self.assertTrue(url)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_I_can_update_a_popit_instance(self):
        '''
        By posting I can update a popit instance and relate
        their persons with a WriteItInstance
        '''
        popit_load_data()
        api_instance = ApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.user,
            )

        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=api_instance,
            )

        url = reverse('rerelate-writeit-popit', kwargs={'pk': record.pk})
        c = Client()
        c.login(username="fieraferoz", password="feroz")
        response = c.post(url)
        self.assertEquals(response.status_code, 200)
        api_instance = ApiInstance.objects.get(id=api_instance.id)
        self.assertTrue(writeitinstance.persons.all())
        self.assertTrue(api_instance.person_set.all())

    def test_I_can_only_access_the_point_if_I_am_logged_in(self):
        '''
        Updating a writeitinstance and a popit instance can only be done
        by someone who is logged in
        '''
        api_instance = ApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.user,
            )

        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=api_instance,
            )

        url = reverse('rerelate-writeit-popit', kwargs={'pk': record.pk})
        c = Client()
        # the following line is intentionally commented
        # c.login(username="fieraferoz", password="feroz")
        response = c.post(url)
        self.assertRedirectToLogin(response, next_url=url)

    def test_I_can_only_access_it_if_I_am_the_owner_of_the_writeitinstance(self):
        '''
        I can update a writeitinstance and a popit instance only if I'm the owner
        of the writeit instance
        '''
        benito = User.objects.create_user(username="benito", password="feroz")
        api_instance = ApiInstance.objects.create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=benito,
            )

        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=writeitinstance,
            popitapiinstance=api_instance,
            )
        url = reverse('rerelate-writeit-popit', kwargs={'pk': record.pk})
        c = Client()
        #fiera is trying to update a
        c.login(username="fieraferoz", password="feroz")

        response = c.post(url)
        self.assertEquals(response.status_code, 403)
        api_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)
        self.assertFalse(api_instance.person_set.all())
        self.assertFalse(writeitinstance.persons.all())

from ...management.commands.back_fill_writeit_popit_records import WPBackfillRecords


class RecreateWriteitInstancePopitInstanceRecord(UserSectionTestCase):
    def setUp(self):
        self.owner = User.objects.first()

    def test_update_creates_records_given_an_instance(self):
        '''Creates a record that relates a writeit instance and a popit instance backwards'''
        w = WriteItInstance.objects.first()
        WPBackfillRecords.back_fill_popit_records(writeitinstance=w)
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 1)

    def test_creates_records_only_once(self):
        '''It creates the records only once'''
        w = WriteItInstance.objects.first()
        a = ApiInstance.objects.first()
        WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=w,
            popitapiinstance=a,
            )
        WPBackfillRecords.back_fill_popit_records(writeitinstance=w)
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 1)

    def test_update_creates_records_given_an_instance_2_persons(self):
        '''
        Creates only one record that relates a writeit instance and a popit instance backwards
        no matter if there are two persons related
        '''
        w = WriteItInstance.objects.first()
        another_person = Person.objects.create(
            api_instance=w.persons.first().api_instance,
            name="Another Person but with the same api Instance",
            )
        Membership.objects.create(writeitinstance=w, person=another_person)
        WPBackfillRecords.back_fill_popit_records(writeitinstance=w)
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 1)

    def test_update_per_user(self):
        '''It can create backward records per user'''
        WPBackfillRecords.back_fill_popit_records_per_user(user=self.owner)
        w = self.owner.writeitinstances.first()
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 1)

    def test_call_command(self):
        '''Call command backward writeit popit records'''

        call_command(
            'back_fill_writeit_popit_records',
            self.owner.username,
            verbosity=0,
            interactive=False,
            )

        w = self.owner.writeitinstances.first()
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 1)

    def test_if_there_is_no_user_given_it_throws_an_error(self):
        '''If there is no username given doesn't throw an error'''

        call_command(
            'back_fill_writeit_popit_records',
            verbosity=0,
            interactive=False,
            )

        w = self.owner.writeitinstances.first()
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 0)

    def test_if_the_user_does_not_exist(self):
        '''If the given user does not exist it doesn't throw any errors'''

        call_command(
            'back_fill_writeit_popit_records',
            "i_dont_exist",
            verbosity=0,
            interactive=False,
            )

        w = self.owner.writeitinstances.first()
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=w)
        self.assertEquals(records.count(), 0)


@skipUnless(settings.LOCAL_POPIT, "No local popit running")
class RelateMyWriteItInstanceWithAPopitInstance(UserSectionTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="fieraferoz", password="feroz")
        self.writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )
        self.data = {"popit_url": settings.TEST_POPIT_API_URL}
        popit_load_data()

    def test_create_form(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)

        self.assertTrue(form)
        self.assertIsInstance(form, Form)

    def test_form_fields(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)
        self.assertIn('popit_url', form.fields)
        self.assertIsInstance(form.fields['popit_url'], URLField)
        self.assertTrue(form.is_valid())

    def test_form_relate(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)
        form.is_valid()
        form.relate()
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=self.writeitinstance)
        self.assertEquals(records.count(), 1)
        self.assertTrue(self.writeitinstance.persons.all())

    def test_url_for_posting_the_url(self):
        url = reverse('relate-writeit-popit', kwargs={'pk': self.writeitinstance.pk})
        self.assertTrue(url)

    def test_post_to_the_url(self):
        '''It should reject the get to that url'''
        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', kwargs={'pk': self.writeitinstance.pk})
        response = self.client.post(url, data=self.data)
        self.assertEquals(response.status_code, 302)
        basic_update_url = reverse('writeitinstance_basic_update', kwargs={'pk': self.writeitinstance.pk})

        self.assertRedirects(response, basic_update_url)

        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=self.writeitinstance)
        self.assertEquals(records.count(), 1)
        # this means that it has persons related to it
        self.assertTrue(self.writeitinstance.persons.all())

    def test_post_to_the_url_shows_includes_something_about_the_result(self):
        '''Posting to relate the popit and writetiinstances returns something abotu the result'''
        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', kwargs={'pk': self.writeitinstance.pk})
        data = self.data
        data['popit_url'] = 'http://nonexistingurl.org'
        response = self.client.post(url, data=data, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(messages)
        self.assertEquals(messages[0].message, _('We could not connect with the URL'))

    def test_insights_about_pulling_popit_even_if_everything_goes_ok(self):
        '''Return some insights even if everything goes ok'''
        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', kwargs={'pk': self.writeitinstance.pk})
        data = self.data
        response = self.client.post(url, data=data, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(messages)
        self.assertEquals(messages[0].message, _('Everything went ok'))

    def test_get_the_url(self):
        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', kwargs={'pk': self.writeitinstance.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'nuntium/profiles/writeitinstance_and_popit_relations.html')
