from django.forms import ModelForm
from django.forms.models import ModelChoiceField
from contactos.models import Contact
from mailit import MailChannel


class ContactUpdateForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['value']


class SelectSinglePersonField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.name, obj.api_instance.url)


class ContactCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance')
        self.person = kwargs.pop('person')
        self.contact_type = MailChannel().contact_type
        super(ContactCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        contact = super(ContactCreateForm, self).save(commit=False)
        contact.writeitinstance = self.writeitinstance
        contact.person = self.person
        contact.contact_type = self.contact_type
        if commit:
            contact.save()
        return contact

    class Meta:
        model = Contact
        fields = ['value']
        widgets = {
        }
