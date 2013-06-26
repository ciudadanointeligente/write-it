from global_test_case import GlobalTestCase as TestCase
from mailit.bin import EmailHandler, EmailAnswer

class AnswerHandlerTestCase(TestCase):
	def test_class_answer(self):
		email_answer = EmailAnswer()
		email_answer.subject = 'prueba4'
		email_answer.content_text = 'prueba4lafieritaespeluda'


		self.assertTrue(email_answer)
		self.assertEquals(email_answer.subject, 'prueba4')
		self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')

class IncomingEmailHandlerTestCase(TestCase):
	def setUp(self):
		f = open('mailit/tests/fixture/mail.txt')
		self.email = f.readlines()
		f.close()
		self.handler = EmailHandler()



	def test_gets_the_subject(self):
		answer = self.handler.handle(self.email)
		self.assertEquals(answer.subject, 'prueba4')
		self.assertTrue(answer.content_text.startswith('prueba4lafieri'))


