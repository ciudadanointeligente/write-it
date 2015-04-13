# coding=utf8
from django.contrib.auth.models import User

from global_test_case import GlobalTestCase as TestCase
from mailit.bin import config
from mailit.bin.handleemail import EmailAnswer
from django.core.files import File
from mock import patch
from mailit.tests.email_parser.incoming_mail_tests import PostMock
from nuntium.models import Answer


class AnswerHandlerTestCase(TestCase):
    def setUp(self):
        super(AnswerHandlerTestCase, self).setUp()
        self.user = User.objects.get(id=1)
        self.where_to_post_creation_of_the_answer = 'http://writeit.ciudadanointeligente.org/api/v1/create_answer/'
        config.WRITEIT_API_ANSWER_CREATION = self.where_to_post_creation_of_the_answer
        config.WRITEIT_API_KEY = self.user.api_key.key
        config.WRITEIT_USERNAME = self.user.username
        self.photo_fiera = File(open("nuntium/tests/fixtures/fiera_parque.jpg", 'rb'))
        self.pdf_file = File(open("nuntium/tests/fixtures/hello.pd.pdf", 'rb'))

    def test_class_answer(self):

        email_answer = EmailAnswer()
        self.assertTrue(hasattr(email_answer, 'subject'))
        self.assertTrue(hasattr(email_answer, '_content_text'))
        self.assertTrue(hasattr(email_answer, 'content_html'))
        self.assertTrue(hasattr(email_answer, 'outbound_message_identifier'))
        self.assertTrue(hasattr(email_answer, 'email_from'))
        self.assertTrue(hasattr(email_answer, 'email_to'))
        self.assertTrue(hasattr(email_answer, 'when'))
        self.assertTrue(hasattr(email_answer, 'message_id'))
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.content_html = '<p>prueba4lafieritaespeluda</p>'
        email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'
        email_answer.email_from = 'falvarez@votainteligente.cl'
        email_answer.email_to = 'Felipe <instance-slug+8974aabsdsfierapulgosa@writeit.org>'
        email_answer.when = 'Wed Jun 26 21:05:33 2013'
        email_answer.message_id = '<CAA5PczfGfdhf29wgK=8t6j7hm8HYsBy8Qg87iTU2pF42Ez3VcQ@mail.gmail.com>'

        self.assertTrue(email_answer)
        self.assertEquals(email_answer.subject, 'prueba4')
        self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')
        self.assertEquals(email_answer.outbound_message_identifier, '8974aabsdsfierapulgosa')
        self.assertEquals(email_answer.email_from, 'falvarez@votainteligente.cl')
        self.assertEquals(email_answer.email_to, 'Felipe <instance-slug+8974aabsdsfierapulgosa@writeit.org>')
        self.assertEquals(email_answer.when, 'Wed Jun 26 21:05:33 2013')
        self.assertEquals(email_answer.message_id, '<CAA5PczfGfdhf29wgK=8t6j7hm8HYsBy8Qg87iTU2pF42Ez3VcQ@mail.gmail.com>')
        self.assertEquals(email_answer.content_html, '<p>prueba4lafieritaespeluda</p>')
        self.assertFalse(email_answer.is_bounced)

    def test_getter_removes_the_identifier(self):
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'
        email_answer.content_text = 'prueba4lafieritaespeluda y lo mandé desde este mail devteam+8974aabsdsfierapulgosa@chile.com'

        self.assertFalse(email_answer.outbound_message_identifier in email_answer.content_text)
        self.assertNotIn("devteam+@chile.com", email_answer.content_text)

    def test_it_doesnt_contain_anything_of_the_original_email(self):
        '''If I set the "To" header in the email and use it in the email_answer.recipient
        then I should not be getting her/his email address in the content'''
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba5'
        email_answer.email_to = 'Tony <instance-2+identifier123@writeit.org>'
        email_answer.outbound_message_identifier = 'identifier123'
        email_answer.content_text = '''Thank you for your enquiry. I am completely in favour of this measure,
and will certainly be voting for it.
Tony 
<instance-2+identifier123@writeit.org>:'''
        # There is an intended extra space after the word 'Tony'
        self.assertNotIn('<instance-', email_answer.content_text)
        self.assertNotIn('> :', email_answer.content_text)
        self.assertNotIn('Tony', email_answer.content_text)

    def test_the_email_answer_can_have_attachments(self):
        '''An email answer can have attachments'''
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.add_attachment(self.photo_fiera)
        email_answer.add_attachment(self.pdf_file)
        self.assertTrue(email_answer.attachments)
        self.assertIn(self.photo_fiera, email_answer.attachments)
        self.assertIn(self.pdf_file, email_answer.attachments)

    def test_save_attachments_on_save(self):
        '''When saving it also calls the save an attachment'''
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.add_attachment(self.photo_fiera)
        email_answer.add_attachment(self.pdf_file)
        any_answer = Answer.objects.first()

        with patch('requests.Session.post') as post:
            post.return_value = PostMock()
            with patch('mailit.bin.handleemail.EmailAnswer.save_attachment') as save_attachment:
                with patch('mailit.bin.handleemail.EmailAnswer.save') as save_answer:
                    save_answer.return_value = any_answer
                    email_answer.send_back()
                    save_attachment.assert_any_call(any_answer, self.photo_fiera)
                    save_attachment.assert_any_call(any_answer, self.pdf_file)
