from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from popit.models import ApiInstance
from contactos.models import Contact



class MessageManager(models.Manager):
    def create(self, **kwargs):
        if 'persons' in kwargs:
            persons = kwargs.pop('persons')
        else:
            raise TypeError('A message needs persons to be sent')
        message = super(MessageManager, self).create(**kwargs)
        for person in persons:
            for contact in person.contact_set.all():
                outbound_message = OutboundMessage.objects.create(contact=contact, message=message)
        return message
		
class WriteItInstance(models.Model):
    """WriteItInstance: Entity that groups messages and people for usability purposes. E.g. 'Candidates running for president'"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    api_instance = models.ForeignKey(ApiInstance)

    @models.permalink
    def get_absolute_url(self):
        return ('instance_detail', (), {'slug': self.slug})


class Message(models.Model):
    """Message: Class that contain the info for a model, despite of the input and the output channels. Subject and content are mandatory fields"""
    STATUS_CHOICES = (
        ("new",_("Newly created")),
        ("sent",_("Sent")),
        )


    subject = models.CharField(max_length=512)
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance)
    status = models.CharField(max_length="4", choices=STATUS_CHOICES, default="new")

    objects = MessageManager()




    def __init__(self, *args, **kwargs):
        self.persons = None
        if 'persons' in kwargs:
            self.persons = kwargs.pop('persons')
        super(Message, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):

        super(Message, self).save(*args, **kwargs)
        if self.persons:
            for person in self.persons:
                for contact in person.contact_set.all():
                    outbound_message = OutboundMessage.objects.create(contact=contact, message=self)


    def send(self):
        self.status = "sent"
        self.save()

class OutboundMessage(models.Model):
    """docstring for OutboundMessage: This class is the message delivery unit. The OutboundMessage is the one that will be tracked in order 
    to know the actual status of the message"""
    contact = models.ForeignKey(Contact)
    message = models.ForeignKey(Message)
		
