from django.forms import ModelForm
from contactos.models import Contact

class ContactUpdateForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['value', ]


class ContactCreateForm(ModelForm):
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
        fields = ['contact_type', 'value','person',]

