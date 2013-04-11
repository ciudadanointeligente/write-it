from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from popit.models import ApiInstance
from contactos.models import Contact


class MessageManager(models.Manager):
    def create(self, **kwargs):
        if 'contacts' in kwargs:
            contacts = kwargs['contacts']
            del kwargs['contacts']
        else:
            raise TypeError('A message needs contacts to be sent')
        message = super(MessageManager, self).create(**kwargs)
        for contact in contacts:
            messageoutbox = MessageOutbox.objects.create(contact=contact, message=message)
        return message

class Message(models.Model):
    """Message: Class that contain the info for a model, despite of the input and the output channels. Subject and content are mandatory fields"""
    subject = models.CharField(max_length=512)
    content = models.TextField()
    instance = models.ForeignKey('Instance')

    objects = MessageManager()

		
class Instance(models.Model):
    """Instance: Entity that groups messages and people for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    api_instance = models.ForeignKey(ApiInstance)

class MessageOutbox(models.Model):
    """docstring for MessageOutbox: This class is the message delivery unit. The MessageOutbox is the one that will be tracked in order 
    to know the actual status of the message"""
    contact = models.ForeignKey(Contact)
    message = models.ForeignKey(Message)
		
