from django.forms import ModelForm, TextInput, Textarea
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from mailit.models import MailItTemplate, default_content_template


class MailitTemplateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            writeitinstance = kwargs.pop("writeitinstance")
        except:
            raise ValidationError(_('Instance not present'))
        self.writeitinstance = writeitinstance

        super(MailitTemplateForm, self).__init__(*args, **kwargs)

        self.initial['content_template'] = self.initial['content_template'] or default_content_template

    def save(self, commit=True):
        if self.cleaned_data['content_template'] == default_content_template:
            self.cleaned_data['content_template'] = None

        template = super(MailitTemplateForm, self).save(commit=False)
        template.writeitinstance = self.writeitinstance

        if commit:
            template.save()
        return template

    class Meta:
        model = MailItTemplate
        fields = ["subject_template", "content_template"]

        widgets = {
            'subject_template': TextInput(attrs={'class': 'form-control'}),
            'content_template': Textarea(attrs={'class': 'form-control'}),
        }
