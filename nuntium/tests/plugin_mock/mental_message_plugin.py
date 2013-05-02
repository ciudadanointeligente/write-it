from nuntium.plugins import OutputPlugin
from nuntium.models import MessageRecord

class MentalMessage(OutputPlugin):
    name = 'mental-message'
    title = 'Mental Message'

    def send(self, outbound_message):
    	try:
    		self.send_mental_message(outbound_message.message.subject)
    	except FatalException:
            #This is right what it should not be doing
            #There could be an error with emails
            #but no error with phone call or fax
    		outbound_message.status = "error"
    		outbound_message.save()
    		return False
    	except TryAgainException:
    		return False

        record = MessageRecord.objects.create(content_object= outbound_message, status="sent using mental messages")
        return True

    def send_mental_message(self, subject):
    	if subject == "RaiseFatalErrorPlz":
    		raise FatalException("FatalException")

    	if subject == "RaiseTryAgainErrorPlz":
    		raise TryAgainException

    	return


class FatalException(Exception):
	pass

class TryAgainException(Exception):
	pass
