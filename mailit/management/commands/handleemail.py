from mailit.bin.handleemail import EmailAnswer, EmailHandler
from mailit.models import BouncedMessageRecord
from nuntium.models import OutboundMessageIdentifier, OutboundMessage
from django.core.management.base import BaseCommand, CommandError
import sys

class AnswerForManageCommand(EmailAnswer):
    def save(self):
        OutboundMessageIdentifier.create_answer(self.outbound_message_identifier, self.content_text)

    def report_bounce(self):
    	identifier = OutboundMessageIdentifier.objects.get(key=self.outbound_message_identifier)
    	outbound_message = OutboundMessage.objects.get(outboundmessageidentifier=identifier)
        BouncedMessageRecord.objects.create(outbound_message=outbound_message, bounce_text=self.content_text)
    	contact = outbound_message.contact
    	contact.is_bounced = True

    	contact.save()

class Command(BaseCommand):
	args = ''
	help = 'Handles incoming EmailAnswer'

	def handle(self, *args, **options):
		lines = sys.stdin.readlines()
		handler = EmailHandler(answer_class = AnswerForManageCommand)
		answer = handler.handle(lines)
		answer.send_back()