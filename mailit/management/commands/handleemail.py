from mailit.bin.handleemail import EmailAnswer, EmailHandler
from mailit.models import BouncedMessageRecord
import logging
from nuntium.models import OutboundMessageIdentifier, OutboundMessage
from django.core.management.base import BaseCommand, CommandError
import sys

logging.basicConfig(filename='mailing_logger.txt', level=logging.INFO)

class AnswerForManageCommand(EmailAnswer):
    def save(self):
        OutboundMessageIdentifier.create_answer(self.outbound_message_identifier, self.content_text)

    def report_bounce(self):
        print "oliiwi"
        logging.info("Reporting bounce using a management command")
        identifier = OutboundMessageIdentifier.objects.get(key=self.outbound_message_identifier)
        outbound_message = OutboundMessage.objects.get(outboundmessageidentifier=identifier)
        outbound_message.status = 'error'
        outbound_message.save()
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