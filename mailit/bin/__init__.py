import email

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
		# print msg["To"]
		for part in msg.walk():
			if part.get_content_type() == 'text/plain':
				answer.content_text = part.get_payload() 
		return answer


class EmailAnswer():
	def __init__(self):
		self.subject = ''
		self.content_text = ''