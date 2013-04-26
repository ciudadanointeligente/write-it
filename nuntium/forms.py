from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple
from nuntium.models import Message, WriteItInstance, OutboundMessage
from contactos.models import Contact
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from popit.models import Person

class PersonMultipleChoiceField(ModelMultipleChoiceField):
    widget = CheckboxSelectMultiple()

    def label_from_instance(self, obj):
        return obj.name

class MessageCreateForm(ModelForm):
    ''' docstring for MessageCreateForm'''
    persons = PersonMultipleChoiceField(queryset=Person.objects.none())


    def __init__(self, *args, **kwargs):
        try:
            writeitinstance = kwargs.pop("writeitinstance")
        except:
            raise ValidationError(_('Instance not present'))        
        self.writeitinstance = writeitinstance
        persons = Person.objects.filter(api_instance=writeitinstance.api_instance)
        super(MessageCreateForm, self).__init__(*args, **kwargs)
        self.fields['persons'].queryset = persons

    def save(self, force_insert=False, force_update=False, commit=True):
        message = super(MessageCreateForm, self).save(commit=False)
        message.writeitinstance = self.writeitinstance
        if commit:
            message.save()
            persons = self.cleaned_data['persons']
            for person in persons:
                for contact in person.contact_set.all():
                    OutboundMessage.objects.create(contact=contact, message=message)

        return message

    class Meta:
        model = Message
        exclude = ("writeitinstance", "status")