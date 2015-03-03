from global_test_case import GlobalTestCase as TestCase
from nuntium.models import Message, Answer, AnswerAttachment
from popit.models import Person
from django.core.files import File


class AnswerAttachmentsTest(TestCase):
    def setUp(self):
        super(AnswerAttachmentsTest, self).setUp()
        self.message = Message.objects.all()[0]
        self.person = Person.objects.all()[0]
        self.answer = Answer.objects.create(
            message=self.message,
            person=self.person,
            content="the answer to that is ..."
            )
        file_ = open("nuntium/tests/fixtures/fiera_parque.jpg", 'rb')
        self.photo_fiera = File(file_)

    def test_instantiate_an_attachment(self):
        '''I can instantiate an attachment'''
        attachment = AnswerAttachment.objects.create(answer=self.answer, content=self.photo_fiera)
        self.assertTrue(attachment)
        self.assertEquals(attachment.answer, self.answer)
        self.assertIn(attachment, self.answer.attachments.all())
