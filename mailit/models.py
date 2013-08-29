from django.db import models
from nuntium.models import WriteItInstance

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

