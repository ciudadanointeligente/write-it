from nuntium.plugins import OutputPlugin

class ManualChannel(OutputPlugin):
	def __init__(self, *args, **kwargs):
		super(ManualChannel, self).__init__(*args, **kwargs)
		self.title = "Manual Contact"
		self.name = "manual"

	def send(self):
		pass