from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Report, Message
from django.core.urlresolvers import reverse


class ReportThisMessageTestCase(TestCase):
    def setUp(self):
        super(ReportThisMessageTestCase, self).setUp()
        # Message with id2 has been confirmed
        self.message = Message.objects.get(id=2)

    def test_a_message_can_have_a_report(self):
        '''A message can have a report which contains a reason'''
        report = Report.objects.create(
            message=self.message,
            reason=u"Because ..."
            )

        self.assertEquals(report.message, self.message)
        self.assertEquals(report.reason, "Because ...")
        self.assertTrue(report.datetime)
        # can a message have several reports?
        # why not?
        report2 = Report.objects.create(
            message=self.message,
            reason=u"Another reason by someone else"
            )
        self.assertEquals(report2.message, self.message)
        self.assertIn(report, self.message.reports.all())
        self.assertIn(report2, self.message.reports.all())


class CreateReportView(TestCase):
    def setUp(self):
        super(CreateReportView, self).setUp()
        # Message with id2 has been confirmed
        self.message = Message.objects.get(id=2)

    def test_get_the_url_for_posting_a_new_report(self):
        '''Get the URL for a new report brings the form'''
        url = reverse('create-report', kwargs={'pk': self.message.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_a_new_report(self):
        url = reverse('create-report', kwargs={'pk': self.message.id})
        data = {
            'reason': "I think that message_2 is offensive"
        }
        response = self.client.post(url, data=data)

        self.assertTrue(self.message.reports.all())
        self.assertEquals(self.message.reports.count(), 1)
        the_report = self.message.reports.first()
        self.assertEquals(the_report.reason, data['reason'])
        instance_url = reverse('instance_detail', kwargs={'slug': self.message.writeitinstance.slug})
        self.assertRedirects(response, instance_url)

    def test_404_when_message_does_not_exist(self):
        '''I get a 404 when a message does not exist'''
        url = reverse('create-report', kwargs={'pk': 144})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
