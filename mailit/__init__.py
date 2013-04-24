from nuntium.plugins import OutputPlugin


class MailChannel(OutputPlugin):
    name = 'mail-channel'
    title = 'Mail Channel'

    def send(self, message):
        return True

