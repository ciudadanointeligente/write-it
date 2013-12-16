from django.forms import ModelForm
from popit.models import Person
from .models import MailItTemplate

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
        fields = ("subject_template", "content_template",)