from django.forms import ModelForm, TextInput, Textarea
from .models import MailItTemplate
from django.forms import ValidationError
from django.utils.translation import ugettext as _


class MailitTemplateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            writeitinstance = kwargs.pop("writeitinstance")
        except:
            raise ValidationError(_('Instance not present'))
        self.writeitinstance = writeitinstance

        super(MailitTemplateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        template = super(MailitTemplateForm, self).save(commit=False)
        template.writeitinstance = self.writeitinstance
        if commit:
            template.save()
        return template

    class Meta:
        model = MailItTemplate
        fields = ("subject_template", "content_template", "content_html_template")

        widgets = {
            'subject_template': TextInput(attrs={'class': 'form-control'}),
            'content_template': Textarea(attrs={'class': 'form-control'}),
            'content_html_template': Textarea(attrs={'class': 'form-control'}),
        }
