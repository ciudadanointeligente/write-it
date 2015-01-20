from django.forms import ModelForm, Select
from django.forms.models import ModelChoiceField
from contactos.models import Contact
from popit.models import Person


class ContactUpdateForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['value']


class SelectSinglePersonField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.name, obj.api_instance.url)


class ContactCreateForm(ModelForm):
    person = SelectSinglePersonField(queryset=Person.objects.all())

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        super(ContactCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        contact = super(ContactCreateForm, self).save(commit=False)
        contact.owner = self.owner
        if commit:
            contact.save()
        return contact

    class Meta:
        model = Contact
        fields = ['contact_type', 'value', 'person']
        widgets = {
            'person': Select(attrs={
                'class': 'chosen-person-select'
                }),
            'contact_type': Select(attrs={
                'class': 'chosen-person-select'
                }),
        }
