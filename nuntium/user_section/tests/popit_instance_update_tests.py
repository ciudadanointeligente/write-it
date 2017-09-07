from global_test_case import popit_load_data
from subdomains.utils import reverse
from instance.models import (
    InstanceMembership, WriteItInstance, WriteitInstancePopitInstanceRecord,
    PopoloPerson)
from popolo_sources.models import PopoloSource
from django.contrib.auth.models import User
from django.forms import Form, URLField
from django.conf import settings
from django.core.management import call_command
from django.utils.unittest import skip
from user_section_views_tests import UserSectionTestCase
from django.utils.translation import ugettext as _
from nuntium.user_section.forms import RelatePopitInstanceWithWriteItInstance
from nuntium.management.commands.back_fill_writeit_popit_records import WPBackfillRecords


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
        p = PopoloSource.objects.first()
        WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=w,
            popolo_source=p,
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
        popolo_source = w.persons.first().popolo_source
        another_person = PopoloPerson.objects.create(
            name="Another Person but with the same Popolo source",
            )
        another_person.add_link_to_popolo_source(popolo_source)
        InstanceMembership.objects.create(writeitinstance=w, person=another_person)
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


class RelateMyWriteItInstanceWithAPopitInstance(UserSectionTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="fieraferoz", password="feroz")
        self.writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )
        self.data = {"popit_url": settings.TEST_POPIT_API_URL}

    @popit_load_data()
    def test_create_form(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)

        self.assertTrue(form)
        self.assertIsInstance(form, Form)

    @popit_load_data()
    def test_form_fields(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)
        self.assertIn('popit_url', form.fields)
        self.assertIsInstance(form.fields['popit_url'], URLField)
        self.assertTrue(form.is_valid())

    @popit_load_data()
    def test_it_parses_the_popit_api(self):
        data = {"popit_url": 'http://the-instance.popit.mysociety.org/api/'}
        form = RelatePopitInstanceWithWriteItInstance(data=data, writeitinstance=self.writeitinstance)
        popit_url = form.get_popit_url_parsed(data["popit_url"])
        expected_url = 'https://the-instance.popit.mysociety.org/api/v0.1'
        self.assertEquals(popit_url, expected_url)
        self.assertTrue(form.is_valid())
        cleaned_data = form.clean()
        self.assertEquals(cleaned_data.get('popit_url'), expected_url)

    @popit_load_data('other_persons')
    def test_the_form_is_not_valid_if_there_is_another_popit(self):
        '''The form is not valid if there is already another popit api instance related'''

        popolo_source = PopoloSource.objects.create(url=settings.TEST_POPIT_API_URL)
        WriteitInstancePopitInstanceRecord.objects.create(writeitinstance=self.writeitinstance,
            popolo_source=popolo_source)

        data = {"popit_url": settings.TEST_POPIT_API_URL}
        form = RelatePopitInstanceWithWriteItInstance(data=data, writeitinstance=self.writeitinstance)
        self.assertFalse(form.is_valid())
        # Ok so because we know that you are trying to update from your previously related popit
        # rather than creating a new one I now should just check that Benito is here
        self.assertTrue(self.writeitinstance.persons.filter(name="Benito"))

    @popit_load_data()
    def test_form_relate(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)
        form.is_valid()
        form.relate()
        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=self.writeitinstance)
        self.assertEquals(records.count(), 1)
        self.assertTrue(self.writeitinstance.persons.all())

    def test_url_for_posting_the_url(self):
        reverse('relate-writeit-popit', subdomain=self.writeitinstance.slug)

    @popit_load_data()
    def test_post_to_the_url(self):
        '''It should reject the get to that url'''
        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', subdomain=self.writeitinstance.slug)
        response = self.client.post(url, data=self.data)
        self.assertEquals(response.status_code, 302)
        basic_update_url = reverse('relate-writeit-popit', subdomain=self.writeitinstance.slug)

        self.assertRedirects(response, basic_update_url)

        records = WriteitInstancePopitInstanceRecord.objects.filter(writeitinstance=self.writeitinstance)
        self.assertEquals(records.count(), 1)
        # this means that it has persons related to it
        self.assertTrue(self.writeitinstance.persons.all())

    @skip("This is very related to issue #411")
    def test_post_to_the_url_shows_includes_something_about_the_result(self):
        '''Posting to relate the popit and writetiinstances returns something abotu the result'''
        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', subdomain=self.writeitinstance.slug)
        data = self.data
        data['popit_url'] = 'http://nonexistingurl.org'
        response = self.client.post(url, data=data, follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(messages)
        self.assertEquals(messages[0].message, _('We could not connect with the URL'))

    def test_get_the_url(self):
        form = RelatePopitInstanceWithWriteItInstance(data=self.data, writeitinstance=self.writeitinstance)
        form.is_valid()
        form.relate()

        self.client.login(username="fieraferoz", password="feroz")
        url = reverse('relate-writeit-popit', subdomain=self.writeitinstance.slug)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('relations', response.context)
        self.assertEquals(len(response.context['relations']), self.writeitinstance.writeitinstancepopitinstancerecord_set.count())
        self.assertTemplateUsed(response, 'nuntium/profiles/writeitinstance_and_popit_relations.html')
        self.assertEquals(response.context['relations'][0], self.writeitinstance.writeitinstancepopitinstancerecord_set.all()[0])
