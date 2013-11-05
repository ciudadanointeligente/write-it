from mailit.bin.handleemail import EmailAnswer, EmailHandler
from mailit.models import BouncedMessageRecord
import logging
from nuntium.models import OutboundMessageIdentifier, OutboundMessage, OutboundMessagePluginRecord
from django.core.management.base import BaseCommand, CommandError
import sys
from django.core.mail import mail_admins
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives

logging.basicConfig(filename='mailing_logger.txt', level=logging.INFO)

class AnswerForManageCommand(EmailAnswer):
    def save(self):
        OutboundMessageIdentifier.create_answer(self.outbound_message_identifier, self.content_text)

    def report_bounce(self):
        logging.info("Reporting bounce using a management command")
        identifier = OutboundMessageIdentifier.objects.get(key=self.outbound_message_identifier)
        outbound_message = OutboundMessage.objects.get(outboundmessageidentifier=identifier)
        outbound_message.status = 'error'
        outbound_message.save()
        records = OutboundMessagePluginRecord.objects.filter(outbound_message=outbound_message)
        for record in records:
            record.try_again = True
            record.save()
        BouncedMessageRecord.objects.create(outbound_message=outbound_message, bounce_text=self.content_text)
        contact = outbound_message.contact
        contact.is_bounced = True
        contact.save()



class Command(BaseCommand):
    args = ''
    help = 'Handles incoming EmailAnswer'

    def handle(self, *args, **options):
        lines = sys.stdin.readlines()
        if settings.INCOMING_EMAIL_LOGGING == 'ALL':
            if not settings.ADMINS:
                return
            text_content = "New incomming email"
            subject = "New incomming email"

            mail = EmailMultiAlternatives('%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject), 
                text_content,#content
                settings.DEFAULT_FROM_EMAIL,#From
                [a[1] for a in settings.ADMINS]#To
                )
            mail.attach('mail.txt', ''.join(lines), 'text/plain')
            mail.send()

        handler = EmailHandler(answer_class = AnswerForManageCommand)
        try:
            answer = handler.handle(lines)
            answer.send_back()
        except Exception, e:
            html_message = '</br> there was an error, and this was the message </ br>'
            for line in lines:
                html_message += line
            mail_admins('Error handling incoming email', html_message, html_message=html_message)
        