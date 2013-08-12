from django.core.management.base import BaseCommand, CommandError
from nuntium.models import OutboundMessage
import logging

logging.basicConfig(filename='send_mails.log', level=logging.INFO)

def send_mails():
    outbound_messages = OutboundMessage.objects.to_send()
    logging.info('Sending messages')
    for outbound_message in outbound_messages:
        result =  outbound_message.send()
        log = 'Sending a message to %(contact)s' % {
            'contact':outbound_message.contact.value
            }
        logging.info(log)


class Command(BaseCommand):
    args = ''
    help = 'Sends all the available mails'

    def handle(self, *args, **options):
        send_mails()