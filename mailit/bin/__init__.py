import email
import re
import requests
import os

class EmailHandler():
	def __init__(self):
		self.message = None

	def handle(self, lines):
		answer = EmailAnswer()
		msgtxt = ''
		for line in lines:
			msgtxt += str(line)

		msg = email.message_from_string(msgtxt)
		answer.subject = msg["Subject"]
		# print msg["Content-Type"]
		regex = re.compile(r".*[\+\-](.*)@.*")

		answer.outbound_message_identifier = regex.match(msg["To"]).groups()[0]
		for part in msg.walk():
			if part.get_content_type() == 'text/plain':
				answer.content_text = part.get_payload() 
		return answer


class EmailAnswer():
	def __init__(self):
		self.subject = ''
		self.content_text = ''
		self.outbound_message_identifier = ''
		self.requests_session = requests.Session()
		username = os.environ['WRITEIT_USERNAME']
		apikey = os.environ['WRITEIT_API_KEY']
		self.requests_session.auth = 'ApiKey %(username)s:%(apikey)s'%{'username':username, 'apikey':apikey}



	def send_back(self):
		data = {
		'key': self.outbound_message_identifier,
		'content': self.content_text
		}
		self.requests_session.post(os.environ['WRITEIT_API_ANSWER_CREATION'], data=data)