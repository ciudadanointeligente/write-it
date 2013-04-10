from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from popit.models import ApiInstance

class Message(models.Model):
    """Message: Class that contain the info for a model, despite of the input and the output channels. Subject and content are mandatory fields"""
    subject = models.CharField(max_length=512)
    content = models.TextField()
    instance = models.ForeignKey('Instance')

		
class Instance(models.Model):
    """Instance: Entity that groups messages and people for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    api_instance = models.ForeignKey(ApiInstance)

		
