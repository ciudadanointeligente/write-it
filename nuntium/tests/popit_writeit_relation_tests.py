# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from ..models import WriteItInstance, Membership
from ..models import WriteitInstancePopitInstanceRecord
from popit.models import ApiInstance
from django.utils.unittest import skipUnless, skip
from django.contrib.auth.models import User
from django.conf import settings
from nuntium.popit_api_instance import PopitApiInstance
from datetime import timedelta
from django.utils import timezone
from mock import patch, call
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class PopitWriteitRelationRecord(TestCase):
    '''
    This set of tests are intended to solve the problem
    of relating a writeit instance and a popit instance
    in some for that does not force them to be
    1-1
    '''
    def setUp(self):
        self.writeitinstance = WriteItInstance.objects.first()
        self.api_instance = ApiInstance.objects.first()
        self.owner = User.objects.first()

    def test_instanciate(self):
        '''Instanciate a WriteitInstancePopitInstanceRelation'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.api_instance,
            )

        self.assertTrue(record)
        self.assertEquals(record.writeitinstance, self.writeitinstance)
        self.assertEquals(record.popitapiinstance, self.api_instance)
        self.assertTrue(record.updated)
        self.assertTrue(record.created)
        self.assertEquals(record.status, 'nothing')
        self.assertEquals(record.periodicity, '1W')  # Weekly
        self.assertFalse(record.status_explanation)

    def test_unicode(self):
        '''A WriteitInstancePopitInstanceRelation has a __unicode__ method'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.api_instance,
            )
        expected_unicode = "The people from http://popit.org/api/v1 were loaded into instance 1"
        self.assertEquals(record.__unicode__(), expected_unicode)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_it_does_not_try_to_replicate_the_memberships(self):
        '''This is related to issue #429'''
        popit_load_data()
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        # Doing it twice so I can replicate the bug
        writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)

        amount_of_memberships = Membership.objects.filter(writeitinstance=writeitinstance).count()

        # There are only 2
        self.assertEquals(amount_of_memberships, 2)
        self.assertEquals(amount_of_memberships, writeitinstance.persons.count())

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_clean_memberships(self):
        '''As part of bug #429 there can be several Membership between one writeitinstance and a person'''
        popit_load_data()
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        # there should be an amount of memberships
        writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        amount_of_memberships = Membership.objects.filter(writeitinstance=writeitinstance).count()
        previous_memberships = list(Membership.objects.filter(writeitinstance=writeitinstance))

        person = writeitinstance.persons.all()[0]

        # Creating a new one
        Membership.objects.create(writeitinstance=writeitinstance, person=person)
        try:
            writeitinstance.relate_with_persons_from_popit_api_instance(popit_api_instance)
        except Membership.MultipleObjectsReturned, e:
            self.fail("There are more than one Membership " + e)

        # It deletes the bad membership
        new_amount_of_memberships = Membership.objects.filter(writeitinstance=writeitinstance).count()
        later_memberships = list(Membership.objects.filter(writeitinstance=writeitinstance))
        self.assertEquals(amount_of_memberships, new_amount_of_memberships)
        self.assertEquals(previous_memberships, later_memberships)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_it_is_created_automatically_when_fetching_a_popit_instance(self):
        '''create automatically a record when fetching a popit instance'''

        popit_load_data()
        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        popit_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)

        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popitapiinstance=popit_instance,
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
        writeitinstance.load_persons_from_a_popit_api(non_existing_url)
        popit_instance_count = ApiInstance.objects.filter(url=non_existing_url).count()

        self.assertFalse(popit_instance_count)

    @skipUnless(settings.LOCAL_POPIT, "No local popit running")
    def test_it_should_be_able_to_update_twice(self):
        '''It should be able to update all data twice'''
        popit_load_data()
        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        popit_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popitapiinstance=popit_instance,
            )

        self.assertNotEqual(record.created, record.updated)

    def test_it_should_update_the_date_every_time_it_is_updated(self):
        '''As described in http://github.com/ciudadanointeligente/write-it/issues/412 the updated date is not updated'''

        popit_load_data()
        # loading data into the popit-api
        writeitinstance = WriteItInstance.objects.create(
            name='instance 1',
            slug='instance-1',
            owner=self.owner,
            )

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)
        popit_instance = ApiInstance.objects.get(url=settings.TEST_POPIT_API_URL)
        record = WriteitInstancePopitInstanceRecord.objects.get(
            writeitinstance=writeitinstance,
            popitapiinstance=popit_instance,
            )
        created_and_updated = timezone.now() - timedelta(days=2)

        record.updated = created_and_updated
        record.created = created_and_updated
        record.save()

        writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)
        record_again = WriteitInstancePopitInstanceRecord.objects.get(id=record.id)
        self.assertNotEqual(record_again.updated, created_and_updated)
        self.assertEquals(record_again.created, created_and_updated)

    def test_set_status(self):
        '''Setting the record status'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.api_instance,
            )

        record.set_status('error', 'Error 404')
        record = WriteitInstancePopitInstanceRecord.objects.get(id=record.id)
        self.assertEquals(record.status, 'error')
        self.assertEquals(record.status_explanation, 'Error 404')

    def test_set_status_in_called_success(self):
        '''In progress and success status called'''
        popit_load_data()
        popit_api_instance, created = PopitApiInstance.objects.get_or_create(url=settings.TEST_POPIT_API_URL)
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)

        with patch.object(WriteitInstancePopitInstanceRecord, 'set_status', return_value=None) as set_status:
            writeitinstance.load_persons_from_a_popit_api(settings.TEST_POPIT_API_URL)

        calls = [call('inprogress'), call('success')]

        set_status.assert_has_calls(calls)

    def test_set_status_in_called_error(self):
        '''In progress and fail status called'''
        writeitinstance = WriteItInstance.objects.create(name='instance 1', slug='instance-1', owner=self.owner)
        non_existing_url = "http://nonexisting.url"
        with patch.object(WriteitInstancePopitInstanceRecord, 'set_status', return_value=None) as set_status:
            writeitinstance.load_persons_from_a_popit_api(non_existing_url)

        calls = [call('inprogress'), call('error', _('We could not connect with the URL'))]

        set_status.assert_has_calls(calls)


class UpdateStatusOfPopitWriteItRelation(TestCase):
    '''
    This test cases should deal with users wanting to:
    * Manually resync their instances
    * How often they want their instances to be resynced
    * Disable syncing of the instance
    '''
    def setUp(self):
        super(UpdateStatusOfPopitWriteItRelation, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.owner = self.writeitinstance.owner
        self.owner.set_password('feroz')
        self.owner.save()
        self.popit_api_instance = PopitApiInstance.objects.first()
        # Empty the popit_api_instance
        self.popit_api_instance.person_set.all().delete()
        self.popit_api_instance.url = settings.TEST_POPIT_API_URL
        self.popit_api_instance.save()
        self.popit_writeit_record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.popit_api_instance
            )

    def test_post_to_the_url_for_manual_resync(self):
        '''Resyncing can be done by posting to a url'''
        # This is just a symbolism but it is to show how this popit api is empty
        self.assertFalse(self.popit_api_instance.person_set.all())

        url = reverse('resync-from-popit', kwargs={'slug': self.writeitinstance.slug,
            'popit_api_pk': self.popit_api_instance.pk})
        self.client.login(username=self.owner.username, password="feroz")
        response = self.client.post(url)
        self.assertEquals(response.status_code, 200)
        # It should have been updated
        self.assertTrue(self.popit_api_instance.person_set.all())

    def test_doesnt_add_another_relation_w_p(self):
        '''
        If a user posts to the server using another popit_api that has not previously been related
        it does not add another relation
        '''
        another_popit_api_instance = PopitApiInstance.objects.last()
        self.assertNotIn(another_popit_api_instance,
            self.writeitinstance.writeitinstancepopitinstancerecord_set.all())

        url = reverse('resync-from-popit', kwargs={'slug': self.writeitinstance.slug,
            'popit_api_pk': another_popit_api_instance.pk})
        self.client.login(username=self.owner.username, password="feroz")
        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)

    def test_post_has_to_be_the_owner_of_the_instance(self):
        '''Only the owner of an instance can resync'''
        url = reverse('resync-from-popit', kwargs={'slug': self.writeitinstance.slug,
            'popit_api_pk': self.popit_api_instance.pk})
        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)

        other_user = User.objects.create_user(username="other_user", password="s3cr3t0")
        self.client.login(username=other_user.username, password='s3cr3t0')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)
