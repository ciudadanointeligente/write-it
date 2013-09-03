from django.db import models
from django.db.models.signals import post_save
from nuntium.models import WriteItInstance, OutboundMessage

# Create your models here.

class MailItTemplate(models.Model):
    subject_template = models.CharField(max_length=255, default="[WriteIT] Message: %(subject)s")
    content_template = models.TextField()
    writeitinstance = models.OneToOneField(WriteItInstance, related_name='mailit_template')

    def __init__(self, *args, **kwargs):
        result = super(MailItTemplate, self).__init__(*args, **kwargs)
        if not self.id and not self.content_template:
            content_template = ''
            with open('mailit/templates/mailit/mails/content_template.txt', 'r') as f:
                content_template += f.read()
            self.content_template = content_template

        return result

def new_write_it_instance(sender,instance, created, **kwargs):
    if created:
        MailItTemplate.objects.create(writeitinstance=instance)
post_save.connect(new_write_it_instance, sender=WriteItInstance)


class BouncedMessageRecord(models.Model):
    outbound_message = models.OneToOneField(OutboundMessage)
    bounce_text = models.TextField()
    date = models.DateTimeField(auto_now=True)

