from django.db import models
from django.db.models.signals import post_save
from nuntium.models import WriteItInstance, OutboundMessage, read_template_as_string,\
    Answer
from django.utils.translation import ugettext_lazy as _

content_template = read_template_as_string(
    'templates/mailit/mails/content_template.txt',
    file_source_path=__file__,
    )


class MailItTemplate(models.Model):
    subject_template = models.CharField(
        max_length=255,
        default="[WriteIT] Message: %(subject)s",
        help_text=_("You can use {{ subject }}, {{ content }}, {{ person }} and {{ author }}"),
        )
    content_template = models.TextField(
        default=content_template,
        help_text=_("You can use {{ subject }}, {{ content }}, {{ person }} and {{ author }}"),
        )
    content_html_template = models.TextField(
        blank=True,
        help_text=_("You can use {{ subject }}, {{ content }}, {{ person }} and {{ author }}"),
        )
    writeitinstance = models.OneToOneField(WriteItInstance, related_name='mailit_template')


def new_write_it_instance(sender, instance, created, **kwargs):
    if created:
        MailItTemplate.objects.create(writeitinstance=instance)
post_save.connect(new_write_it_instance, sender=WriteItInstance)


class BouncedMessageRecord(models.Model):
    outbound_message = models.OneToOneField(OutboundMessage)
    bounce_text = models.TextField()
    date = models.DateTimeField(auto_now=True)


class RawIncomingEmail(models.Model):
    content = models.TextField()
    writeitinstance = models.ForeignKey(WriteItInstance, related_name='raw_emails', null=True)
    answer = models.OneToOneField(Answer, related_name='raw_email', null=True)
    problem = models.BooleanField(default=False)
    message_id = models.CharField(max_length=2048, default="")
