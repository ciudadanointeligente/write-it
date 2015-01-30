# coding=utf-8
from global_test_case import GlobalTestCase as TestCase, popit_load_data
from ..models import WriteItInstance, Membership
from ..models import WriteitInstancePopitInstanceRecord
from popit.models import ApiInstance
from django.utils.unittest import skipUnless, skip
from django.contrib.auth.models import User
from django.conf import settings
from nuntium.popit_api_instance import PopitApiInstance


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
        self.assertTrue(record.autosync)
        self.assertEquals(record.status, 'new')
        self.assertFalse(record.status_explanation)

    def test_unicode(self):
        '''A WriteitInstancePopitInstanceRelation has a __unicode__ method'''
        record = WriteitInstancePopitInstanceRecord.objects.create(
            writeitinstance=self.writeitinstance,
            popitapiinstance=self.api_instance,
            )
        expected_unicode = "The people from http://popit.org/api/v1 was loaded into instance 1"
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
