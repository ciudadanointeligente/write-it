from mailit.bin.handleemail import EmailAnswer, EmailHandler
from mailit.models import BouncedMessageRecord
import logging
from nuntium.models import OutboundMessageIdentifier, OutboundMessage, OutboundMessagePluginRecord, AnswerAttachment
from django.core.management.base import BaseCommand
import sys
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
import traceback
from django.core.files import File
from mailit.exceptions import CouldNotFindIdentifier, TemporaryFailure

logging.basicConfig(filename='mailing_logger.txt', level=logging.INFO)


class AnswerForManageCommand(EmailAnswer):
    def save(self):
        answer = OutboundMessageIdentifier.create_answer(self.outbound_message_identifier, self.content_text)
        return answer

    def save_attachment(self, answer, attachment):
        the_file = File(attachment)
        answer_attachment = AnswerAttachment(answer=answer,
                                content=the_file,
                                name=attachment.name)
        answer_attachment.save()

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
                text_content,  # content
                settings.DEFAULT_FROM_EMAIL,  # From
                [a[1] for a in settings.ADMINS]  # To
                )
            mail.attach('mail.txt', ''.join(lines), 'text/plain')
            mail.send()

        handler = EmailHandler(answer_class=AnswerForManageCommand)
        try:
            answer = handler.handle(lines)
            answer.send_back()
        except CouldNotFindIdentifier:
            pass
        except TemporaryFailure:
            pass
        except:
            tb = traceback.format_exc()
            text_content = "Error the traceback was:\n" + tb
            #mail_admins('Error handling incoming email', html_message, html_message=html_message)
            subject = "Error handling incoming email"
            mail = EmailMultiAlternatives('%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject),
                text_content,  # content
                settings.DEFAULT_FROM_EMAIL,  # From
                [a[1] for a in settings.ADMINS],  # To
                )
            mail.attach('mail.txt', ''.join(lines), 'text/plain')
            mail.send()
