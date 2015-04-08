from global_test_case import GlobalTestCase as TestCase
from nuntium.models import WriteItInstance
from subdomains.utils import reverse
from nuntium.user_section.stats import StatsPerInstance


class StatsPageTestCase(TestCase):
    def setUp(self):
        super(StatsPageTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)
        self.writeitinstance.owner.set_password('feroz')
        self.writeitinstance.owner.save()

    def test_there_is_a_url(self):
        '''There is a url for stats per instance'''
        url = reverse('stats', subdomain=self.writeitinstance.slug)
        self.assertTrue(url)

    def test_get_the_url_brings_the_instance_and_renders_the_template(self):
        '''When getting the url brings some stats and renders the specific template'''
        url = reverse('stats', subdomain=self.writeitinstance.slug)
        self.client.login(username=self.writeitinstance.owner, password="feroz")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('writeitinstance', response.context)
        self.assertTemplateUsed(response, 'nuntium/profiles/stats.html')

    def test_it_brings_some_stats_as_well(self):
        '''It brings some stats as well'''
        url = reverse('stats', subdomain=self.writeitinstance.slug)
        client = self.client
        client.login(username=self.writeitinstance.owner, password="feroz")
        response = client.get(url)
        self.assertIn('stats', response.context)
        stats = response.context['stats']
        self.assertIsInstance(stats, StatsPerInstance)
        self.assertEquals(stats.writeitinstance, self.writeitinstance)


class StatsPerInstanceTestCase(TestCase):
    def setUp(self):
        super(StatsPerInstanceTestCase, self).setUp()
        self.writeitinstance = WriteItInstance.objects.get(id=1)

    def test_instantiate(self):
        '''I can instanciate a StatsPerInstance class with or without an instance'''
        stats = StatsPerInstance()
        self.assertTrue(stats)
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)
        self.assertTrue(stats)
        self.assertEquals(stats.writeitinstance, self.writeitinstance)

    def test_calculate_the_amount_of_messages(self):
        '''It has a property that brings the amount of messages'''
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)
        # It is not explicit but this instance has 3 messages
        self.assertEquals(stats.amount_of_messages, self.writeitinstance.message_set.count())

    def test_stats_public_messages(self):
        '''The stats also include the number of public messages'''
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)
        #it is not explicit but this instance has 2 public messages
        self.assertEquals(stats.amount_of_public_messages, 2)
        self.assertIn(('Total public messages', stats.amount_of_public_messages), stats.get_stats())

    def test_it_should_have_a_list_of_possible_stats(self):
        '''It should have a list of possible stats that can be calculated'''
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)

        statistics = stats.get_stats()
        self.assertTrue(statistics)
        self.assertIn(('Total messages', stats.amount_of_messages), statistics)

    def test_private_messages(self):
        '''It should bring all the private messages'''
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)
        self.assertEquals(stats.amount_of_private_messages, 1)

        statistics = stats.get_stats()
        self.assertTrue(statistics)
        self.assertIn(('Total private messages', stats.amount_of_private_messages), statistics)

    def test_messages_with_answers(self):
        '''It should bring the amount of messages that a person has responded to
        and are public'''
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)
        # it is not explicit but comming from the fixtures
        # the messages with answers are:
        # id: 2, subject: Subject 2
        # id: 3, subject: This is private
        # And the former should not count as it is not public
        self.assertEquals(stats.public_messages_with_answers, 1)
        statistics = stats.get_stats()
        self.assertIn(('Public messages with answers', stats.public_messages_with_answers), statistics)

    def test_confirmed_messages(self):
        '''Listing the confirmed messages'''
        stats = StatsPerInstance(writeitinstance=self.writeitinstance)
        # According to the fixtures there are 1 out of 2 confirmed
        # public messages in this instance
        # There is one private message that we are not taking into account
        self.assertEquals(stats.public_confirmed_messages, 1)
        statistics = stats.get_stats()
        self.assertIn(('Confirmed public messages', stats.public_confirmed_messages), statistics)
