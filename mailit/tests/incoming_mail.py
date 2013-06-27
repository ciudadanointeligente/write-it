from global_test_case import GlobalTestCase as TestCase
from mailit.bin import EmailHandler, EmailAnswer
from django.utils.unittest import skip

class AnswerHandlerTestCase(TestCase):
	def test_class_answer(self):
		email_answer = EmailAnswer()
		email_answer.subject = 'prueba4'
		email_answer.content_text = 'prueba4lafieritaespeluda'
		email_answer.outbound_message_identifier = '8974aabsdsfierapulgosa'


		self.assertTrue(email_answer)
		self.assertEquals(email_answer.subject, 'prueba4')
		self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')
		self.assertEquals(email_answer.outbound_message_identifier, '8974aabsdsfierapulgosa')

class IncomingEmailHandlerTestCase(TestCase):
	def setUp(self):
		f = open('mailit/tests/fixture/mail.txt')
		self.email = f.readlines()
		f.close()
		self.handler = EmailHandler()
		self.answer = self.handler.handle(self.email)
		



	def test_gets_the_subject(self):
		self.assertEquals(self.answer.subject, 'prueba4')

	def test_gets_the_content(self):
		self.assertTrue(self.answer.content_text.startswith('prueba4lafieri'))
		
	def test_gets_the_outbound_message_identifier_to_which_relate_it(self):
		#make a regexp
		#ask maugsbur about it
		self.assertEquals(self.answer.outbound_message_identifier,"4aaaabbb")



