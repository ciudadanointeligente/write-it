from django.core.management.base import BaseCommand
from ...models import OutboundMessage
import logging

logging.basicConfig(filename='send_mails.log', level=logging.INFO)


def send_mails():
    outbound_messages = OutboundMessage.objects.to_send()
    logging.info('Sending messages')
    for outbound_message in outbound_messages:
        outbound_message.send()
        log = 'Sending "%(message)s" to %(contact)s and the result is %(status)s' % {
            'contact': outbound_message.contact.value,
            'message': outbound_message.__unicode__(),
            'status': outbound_message.status
            }
        logging.info(log)


class Command(BaseCommand):
    args = ''
    help = 'Sends all the available mails'

    def handle(self, *args, **options):
        send_mails()
