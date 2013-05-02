from nuntium.plugins import OutputPlugin
from nuntium.models import MessageRecord
'''
This is a mock and should not be used anywhere but as a joke to tell your friends,
One day this kind of messages are going to be normal 
'''

class MentalMessage(OutputPlugin):
    name = 'mental-message'
    title = 'Mental Message'

    def send(self, outbound_message):
        '''
        This function should return some sort of tuple
        indicating if the message was successfully sent and
        if not, it should indicate if the error was fatal or tryagain

        returns (successfully_sent, fatal_error)
        '''
    	try:
    		self.send_mental_message(outbound_message.message.subject)
    	except FatalException:
    		return (False,True)
    	except TryAgainException:
    		return (False, False)

        record = MessageRecord.objects.create(content_object= outbound_message, status="sent using mental messages")
        return (True, None)

    def send_mental_message(self, subject):
    	if subject == "RaiseFatalErrorPlz":
    		raise FatalException

    	if subject == "RaiseTryAgainErrorPlz":
    		raise TryAgainException

    	return


class FatalException(Exception):
	pass

class TryAgainException(Exception):
	pass
