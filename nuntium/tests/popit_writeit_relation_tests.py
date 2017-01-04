# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from instance.models import (
    InstanceMembership, WriteItInstance, WriteitInstancePopitInstanceRecord,
    PopoloPerson)
from popolo_sources.models import PopoloSource
from django.utils.unittest import skip
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from mock import patch, call
from django.utils.translation import ugettext_lazy as _
from subdomains.utils import reverse
from nuntium.user_section.forms import WriteItPopitUpdateForm
from django.test import RequestFactory
from nuntium.user_section.views import ReSyncFromPopit
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
import json


class PopitWriteitRelationRecord(TestCase):
    '''
    This set of tests are intended to solve the problem
    of relating a writeit instance and a popit instance
    in some for that does not force them to be
    1-1
    '''
    def setUp(self):
        self.writeitinstance = WriteItInstance.objects.first()
        self.popolo_source = PopoloSource.objects.first()
        self.owner = User.objects.first()

    def test_instanciate(self):
        '''Instanciate a WriteitInstancePopitInstanceRelation'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popolo_source=self.popolo_source,
            )

        self.assertTrue(record)
        self.assertEquals(record.writeitinstance, self.writeitinstance)
        self.assertEquals(record.popolo_source, self.popolo_source)
        self.assertTrue(record.updated)
        self.assertTrue(record.created)
        self.assertEquals(record.status, 'nothing')
        self.assertEquals(record.periodicity, '1W')  # Weekly
        self.assertFalse(record.status_explanation)

    def test_unicode(self):
        '''A WriteitInstancePopitInstanceRelation has a __unicode__ method'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popolo_source=self.popolo_source,
            )
        expected_unicode = "The people from http://popit.org/api/v1 were loaded into instance 1"
        self.assertEquals(record.__unicode__(), expected_unicode)

    @popit_load_data()
    def test_it_does_not_try_to_replicate_the_memberships(self):
        '''This is related to issue #429'''
        popolo_source, created = PopoloSource.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        # Doing it twice so I can replicate the bug
        writeitinstance.relate_with_persons_from_popolo_json(popolo_source)
        writeitinstance.relate_with_persons_from_popolo_json(popolo_source)

        amount_of_memberships = InstanceMembership.objects.filter(writeitinstance=writeitinstance).count()

        # There are only 2
        self.assertEquals(amount_of_memberships, 2)
        self.assertEquals(amount_of_memberships, writeitinstance.persons.count())

    @popit_load_data()
    def test_clean_memberships(self):
        '''As a result of #429 there might be several Membership between one writeitinstance and a person'''
        popolo_source, created = PopoloSource.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        # there should be an amount of memberships
        writeitinstance.relate_with_persons_from_popolo_json(popolo_source)
        amount_of_memberships = InstanceMembership.objects.filter(writeitinstance=writeitinstance).count()
        previous_memberships = list(InstanceMembership.objects.filter(writeitinstance=writeitinstance))

        person = writeitinstance.persons.all()[0]

        # Creating a new one
        InstanceMembership.objects.create(writeitinstance=writeitinstance, person=person)
        try:
            with popit_load_data():
                writeitinstance.relate_with_persons_from_popolo_json(popolo_source)
        except InstanceMembership.MultipleObjectsReturned, e:
            self.fail("There are more than one InstanceMembership " + e)

        # It deletes the bad membership
        new_amount_of_memberships = InstanceMembership.objects.filter(writeitinstance=writeitinstance).count()
        later_memberships = list(InstanceMembership.objects.filter(writeitinstance=writeitinstance))
        self.assertEquals(amount_of_memberships, new_amount_of_memberships)
        self.assertEquals(previous_memberships, later_memberships)

    @popit_load_data()
    def test_it_is_created_automatically_when_fetching_a_popit_instance(self):
        '''create automatically a record when fetching a popit instance'''

        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        writeitinstance.load_persons_from_popolo_json(settings.TEST_POPIT_API_URL)

        popolo_source = PopoloSource.objects.get(url=settings.TEST_POPIT_API_URL)

        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popolo_source=popolo_source,
            )

        self.assertTrue(record)
        self.assertTrue(record.updated)
        self.assertTrue(record.created)

    @skip("I'm waiting until I solve issue #420")
    def test_what_if_the_url_doesnt_exist(self):
        '''It solves the problem when there is no popit api running'''
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        non_existing_url = "http://nonexisting.url"
        writeitinstance.load_persons_from_popolo_json(non_existing_url)
        popolo_source_count = PopoloSource.objects.filter(url=non_existing_url).count()

        self.assertFalse(popolo_source_count)

    @popit_load_data()
    def test_it_should_be_able_to_update_twice(self):
        '''It should be able to update all data twice'''
        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        writeitinstance.load_persons_from_popolo_json(settings.TEST_POPIT_API_URL)

        popolo_source = PopoloSource.objects.get(url=settings.TEST_POPIT_API_URL)

        writeitinstance.load_persons_from_popolo_json(settings.TEST_POPIT_API_URL)

        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popolo_source=popolo_source,
            )

        self.assertNotEqual(record.created, record.updated)

    @popit_load_data()
    def test_record_updated_should_be_updated_using_inner_function(self):
        '''It should be able to update all data twice'''
        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        popolo_source, _ = PopoloSource.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance._load_persons_from_popolo_json(popolo_source)
        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popolo_source=popolo_source,
            )
        updated_after_first = record.updated
        writeitinstance._load_persons_from_popolo_json(popolo_source)
        record = WriteitInstancePopitInstanceRecord.objects.get(pk=record.id)
        updated_after_second = record.updated

        self.assertNotEqual(updated_after_first, updated_after_second)

    @popit_load_data()
    def test_it_should_update_the_date_every_time_it_is_updated(self):
        '''As described in http://github.com/ciudadanointeligente/write-it/issues/412 the updated date is not updated'''
        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        writeitinstance.load_persons_from_popolo_json(settings.TEST_POPIT_API_URL)
        popolo_source = PopoloSource.objects.get(url=settings.TEST_POPIT_API_URL)
        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popolo_source=popolo_source,
            )
        created_and_updated = timezone.now() - timedelta(days=2)

        record.updated = created_and_updated
        record.created = created_and_updated
        record.save()

        writeitinstance.load_persons_from_popolo_json(settings.TEST_POPIT_API_URL)
        record_again = WriteitInstancePopitInstanceRecord.objects.get(id=record.id)
        self.assertNotEqual(record_again.updated, created_and_updated)
        self.assertEquals(record_again.created, created_and_updated)

    def test_set_status(self):
        '''Setting the record status'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popolo_source=self.popolo_source,
            )

        record.set_status('error', 'Error 404')
        record = WriteitInstancePopitInstanceRecord.objects.get(id=record.id)
        self.assertEquals(record.status, 'error')
        self.assertEquals(record.status_explanation, 'Error 404')

    @popit_load_data()
    def test_set_status_in_called_success(self):
        '''In progress and success status called'''
        popolo_source, created = PopoloSource.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        with patch.object(WriteitInstancePopitInstanceRecord, 'set_status', return_value=None) as set_status:
            writeitinstance.load_persons_from_popolo_json(settings.TEST_POPIT_API_URL)

        calls = [call('inprogress'), call('success')]

        set_status.assert_has_calls(calls)

    def test_set_status_in_called_error(self):
        '''In progress and fail status called'''
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        non_existing_url = "http://nonexisting.url"
        with patch.object(WriteitInstancePopitInstanceRecord, 'set_status', return_value=None) as set_status:
            writeitinstance.load_persons_from_popolo_json(non_existing_url)

        calls = [call('inprogress'), call('error', _('We could not connect with the URL'))]

        set_status.assert_has_calls(calls)


class WriteItPopitTestCase(TestCase):
    def setUp(self):
        super(WriteItPopitTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.owner = self.writeitinstance.owner
        self.owner.set_password('feroz')
        self.owner.save()
        self.popolo_source = PopoloSource.objects.first()
        # Empty the popit_api_instance
        PopoloPerson.objects.origin(self.popolo_source).delete()
        self.popolo_source.url = settings.TEST_POPIT_API_URL
        self.popolo_source.save()
        self.popit_writeit_record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popolo_source=self.popolo_source
            )
        self.request_factory = RequestFactory()


class UpdateStatusOfPopitWriteItRelation(WriteItPopitTestCase):
    '''
    This test cases should deal with users wanting to:
    * Manually resync their instances
    * How often they want their instances to be resynced
    * Disable syncing of the instance
    '''
    def setUp(self):
        super(UpdateStatusOfPopitWriteItRelation, self).setUp()

    @popit_load_data()
    def test_post_to_the_url_for_manual_resync(self):
        '''Resyncing can be done by posting to a url'''
        # This is just a symbolism but it is to show how this popit api is empty
        self.assertFalse(PopoloPerson.objects.origin(self.popolo_source))
        url = reverse('resync-from-popit', subdomain=self.writeitinstance.slug, kwargs={
            'popolo_source_pk': self.popolo_source.pk})
        request = self.request_factory.post(url)
        request.subdomain = self.writeitinstance.slug
        request.user = self.owner
        response = ReSyncFromPopit.as_view()(request, popolo_source_pk=self.popolo_source.pk)

        self.assertEquals(response.status_code, 200)
        # It should have been updated
        self.assertTrue(PopoloPerson.objects.origin(self.popolo_source))

    @popit_load_data()
    def test_doesnt_add_another_relation_w_p(self):
        '''
        If a user posts to the server using another popolo source that has not previously been related
        it does not add another relation
        '''
        another_popolo_source = PopoloSource.objects.last()
        self.assertNotIn(another_popolo_source,
            self.writeitinstance.writeitinstancepopitinstancerecord_set.all())

        url = reverse('resync-from-popit', subdomain=self.writeitinstance.slug, kwargs={
            'popolo_source_pk': another_popolo_source.pk})
        request = self.request_factory.post(url)
        request.subdomain = self.writeitinstance.slug
        request.user = self.owner
        with self.assertRaises(Http404):
            ReSyncFromPopit.as_view()(request, popolo_source_pk=another_popolo_source.pk)

    def test_post_has_to_be_the_owner_of_the_instance(self):
        '''Only the owner of an instance can resync'''
        url = reverse('resync-from-popit', subdomain=self.writeitinstance.slug, kwargs={
            'popolo_source_pk': self.popolo_source.pk})
        request = self.request_factory.post(url)
        request.subdomain = self.writeitinstance.slug
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            ReSyncFromPopit.as_view()(request, popolo_source_pk=self.popolo_source.pk)

        other_user = User.objects.create_user(username="other_user", password="s3cr3t0")

        request = self.request_factory.post(url)
        request.subdomain = self.writeitinstance.slug
        request.user = other_user
        with self.assertRaises(Http404):
            ReSyncFromPopit.as_view()(request, popolo_source_pk=self.popolo_source.pk)

from nuntium.user_section.views import WriteItPopitUpdateView


class UpdateRecordFormTestCase(WriteItPopitTestCase):
    '''
    This deals with a Form to update the periodicity of syncronization of an instance
    '''
    def setUp(self):
        super(UpdateRecordFormTestCase, self).setUp()

    def test_validate_the_form(self):
        data = {'periodicity': '1D'}
        form = WriteItPopitUpdateForm(data, instance=self.popit_writeit_record)
        self.assertIn('periodicity', form.fields)
        self.assertTrue(form.is_valid())

    def test_posting_a_new_value_to_the_url_updates_the_value(self):
        url = reverse('update-popit-writeit-relation',
                subdomain=self.writeitinstance.slug,
                kwargs={
                    'pk': self.popit_writeit_record.pk
                }
            )
        request = self.request_factory.post(url)
        request.subdomain = self.writeitinstance.slug
        request.user = self.owner
        request.POST = {'periodicity': '1D'}
        # This is the result of posting
        response = WriteItPopitUpdateView.as_view()(request, pk=self.popit_writeit_record.pk)
        # I'm hoping this to be an ajax call
        self.assertEquals(response.status_code, 200)
        response_object = json.loads(response.content)
        self.assertEquals(response_object['id'], self.popit_writeit_record.pk)
        self.assertEquals(response_object['periodicity'], '1D')
        # This is the expected result
        record = WriteitInstancePopitInstanceRecord.objects.get(id=self.popit_writeit_record.pk)
        self.assertEquals(record.periodicity, '1D')

    def test_form_invalid(self):
        url = reverse('update-popit-writeit-relation',
                subdomain=self.writeitinstance.slug,
                kwargs={
                    'pk': self.popit_writeit_record.pk
                }
            )
        request = self.request_factory.post(url)
        request.subdomain = self.writeitinstance.slug
        request.user = self.owner
        request.POST = {'periodicity': 'invalid'}
        response = WriteItPopitUpdateView.as_view()(request, pk=self.popit_writeit_record.pk)
        # I'm hoping this to be an ajax call
        self.assertEquals(response.status_code, 200)
        response_object = json.loads(response.content)
        self.assertTrue(response_object['errors'])

    def test_cannot_get_it_should_return_405(self):
        url = reverse('update-popit-writeit-relation',
                subdomain=self.writeitinstance.slug,
                kwargs={
                    'pk': self.popit_writeit_record.pk
                }
            )
        request = self.request_factory.get(url)
        request.subdomain = self.writeitinstance.slug
        request.user = self.owner
        request.GET = {'periodicity': 'invalid'}
        response = WriteItPopitUpdateView.as_view()(request, pk=self.popit_writeit_record.pk)
        self.assertEquals(response.status_code, 405)
