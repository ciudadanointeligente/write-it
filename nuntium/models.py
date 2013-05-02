from django.db.models.signals import post_save
from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from popit.models import ApiInstance
from contactos.models import Contact
from nuntium.plugins import OutputPlugin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
from djangoplugins.models import Plugin



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

    def __unicode__(self):
        return self.name

class MessageRecord(models.Model):
    status = models.CharField(max_length=255)
    datetime = models.DateField(default=datetime.datetime.now())
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        outbound_message = self.content_object
        return _('The message "%(subject)s" at %(instance)s turned %(status)s at %(date)s') % {
            'subject': outbound_message.message.subject,
            'instance': outbound_message.message.writeitinstance,
            'status': self.status,
            'date' : str(self.datetime)
            }


class Message(models.Model):
    """Message: Class that contain the info for a model, despite of the input and the output channels. Subject and content are mandatory fields"""
    STATUS_CHOICES = (
        ("new",_("Newly created")),
        ("sent",_("Sent")),
        )


    subject = models.CharField(max_length=512)
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance)
    #status = models.CharField(max_length="4", choices=STATUS_CHOICES, default="new")

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

    def __unicode__(self):
        return _('%(subject)s at %(instance)s') % {
            'subject':self.subject,
            'instance':self.writeitinstance.name
            }


class OutboundMessageManager(models.Manager):
    def to_send(self, *args, **kwargs):
        query = super(OutboundMessageManager, self).filter(*args, **kwargs)
        return query.filter(status="ready")



class OutboundMessage(models.Model):
    """docstring for OutboundMessage: This class is the message delivery unit. The OutboundMessage is the one that will be tracked in order 
    to know the actual status of the message"""

    STATUS_CHOICES = (
        ("new",_("Newly created")),
        ("ready",_("Ready to send")),
        ("sent",_("Sent")),
        ("error",_("Error sending it")),
        )

    contact = models.ForeignKey(Contact)
    message = models.ForeignKey(Message)
    status = models.CharField(max_length="10", choices=STATUS_CHOICES, default="ready")

    objects = OutboundMessageManager()

    def __unicode__(self):
        return _('%(subject)s sent to %(person)s (%(contact)s) at %(instance)s') % {
            'subject': self.message.subject,
            'person':self.contact.person.name,
            'contact':self.contact.value,
            'instance':self.message.writeitinstance.name
        }
	
    def send(self):
        if self.status == "sent":
            return False
        self.status="sent"
        self.save()
        plugins = OutputPlugin.get_plugins()
        MessageRecord.objects.create(content_object= self, status=self.status)
        for plugin in plugins:
            #I should keep a record of what has been sent to someone trough which channel
            #and know if I should send again
            plugin.send(self)
            #Also here comes what should be any priorization on the channels
            #that I'm not workin on right now
            #and it should send to all of them
            #should I have another state "partly sent"? or is it enough when I say "ready"?
        #I have an error right here why is it returning true all the time
        return True


def create_a_message_record(sender,instance, created, **kwargs):
    outbound_message = instance
    if created:
        MessageRecord.objects.create(content_object= outbound_message, status=outbound_message.status)
post_save.connect(create_a_message_record, sender=OutboundMessage)


class OutboundMessagePluginRecord(models.Model):
    outbound_message = models.ForeignKey(OutboundMessage)
    plugin = models.ForeignKey(Plugin)
    sent = models.BooleanField()