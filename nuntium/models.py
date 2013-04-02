from django.db import models

class Message(models.Model):
	"""Message: Class that contain the info for a model, despite the inputo and the output channels."""
	content = models.TextField()
	
		
