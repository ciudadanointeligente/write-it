from django.forms import ModelForm
from contactos.models import Contact

class ContactUpdateForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['value', ]