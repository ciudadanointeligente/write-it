from nuntium.plugins import OutputPlugin
from nuntium.models import MessageRecord

class MentalMessage(OutputPlugin):
    name = 'mental-message'
    title = 'Mental Message'

    def send(self, outbound_message):
        record = MessageRecord.objects.create(content_object= outbound_message, status="sent using mental messages")
        return
