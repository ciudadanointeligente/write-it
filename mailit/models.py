from django.db import models
from nuntium.models import WriteItInstance

# Create your models here.

class MailItTemplate(models.Model):
    subject_template = models.CharField(max_length=255)
    content_template = models.TextField()
    writeitinstance = models.OneToOneField(WriteItInstance, related_name='mailit_template')
