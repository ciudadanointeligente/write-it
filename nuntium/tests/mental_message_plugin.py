from nuntium.plugins import OutputPlugin

class MentalMessage(OutputPlugin):
    name = 'mental-message'
    title = 'Mental Message'

    def send(self, message):
        message.content = u"bz-bz sent using psychokinesis"
        message.save()
        return
