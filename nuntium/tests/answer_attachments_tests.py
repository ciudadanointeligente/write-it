from global_test_case import GlobalTestCase as TestCase
from instance.models import PopoloPerson
from nuntium.models import Message, Answer, AnswerAttachment
from django.core.files import File
from subdomains.utils import reverse


class AnswerAttachmentsTest(TestCase):
    def setUp(self):
        super(AnswerAttachmentsTest, self).setUp()
        self.message = Message.objects.all()[0]
        self.person = PopoloPerson.objects.all()[0]
        self.answer = Answer.objects.create(
            message=self.message,
            person=self.person,
            content="the answer to that is ..."
            )
        self.photo_fiera = File(open("nuntium/tests/fixtures/fiera_parque.jpg", 'rb'))
        self.pdf_file = File(open("nuntium/tests/fixtures/hello.pd.pdf", 'rb'))

    def test_instantiate_an_attachment(self):
        '''I can instantiate an attachment'''
        attachment = AnswerAttachment.objects.create(answer=self.answer,
                        content=self.photo_fiera,
                        name="fiera_parque.jpg")
        self.assertTrue(attachment)
        self.assertEquals(attachment.answer, self.answer)
        self.assertIn(attachment, self.answer.attachments.all())

    def test_there_is_a_url_for_this_attachment(self):
        '''There is a url for an attachment'''
        attachment = AnswerAttachment.objects.create(answer=self.answer, content=self.photo_fiera)
        url = reverse('attachment', subdomain=self.message.writeitinstance.slug, kwargs={
            'pk': attachment.pk,
            })
        response = self.client.get(url)
        self.assertIn('attachment', response.get('Content-Disposition'))
        self.assertIn('filename=fiera_parque', response.get('Content-Disposition'))
        self.assertIn('.jpg', response.get('Content-Disposition'))

    def test_using_a_pdf(self):
        '''Downloading a PDF file'''
        attachment = AnswerAttachment.objects.create(answer=self.answer, content=self.pdf_file)
        url = reverse('attachment', subdomain=self.message.writeitinstance.slug, kwargs={
            'pk': attachment.pk,
            })
        response = self.client.get(url)
        self.assertIn('attachment', response.get('Content-Disposition'))
        self.assertIn('filename=hello.pd', response.get('Content-Disposition'))
        self.assertIn('.pdf', response.get('Content-Disposition'))
