from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple
from nuntium.models import Message, Instance, OutboundMessage
from contactos.models import Contact
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from popit.models import Person

class MessageCreateForm(ModelForm):
    ''' docstring for MessageCreateForm'''
    persons = ModelMultipleChoiceField(queryset=Person.objects.none(), \
                                        widget=CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        super(MessageCreateForm, self).__init__(*args, **kwargs)
        if len(args)>0 and 'instance' in args[0]:
            instance_id = args[0]['instance']

            kwargs['instance'] = Instance.objects.get(id=instance_id)

        if 'instance' not in kwargs:
            raise ValidationError(_('Instance not present'))
        self.instance1 = kwargs['instance']
        persons = Person.objects.filter(api_instance=self.instance1.api_instance)
        self.fields['persons'].queryset = persons

    def clean(self):
        data = self.cleaned_data
        data['instance'] = self.instance1
        return data

    def save(self, force_insert=False, force_update=False, commit=True):
        message = super(MessageCreateForm, self).save(commit=commit)
        if commit:
            persons = self.cleaned_data['persons']
            for person in persons:
                for contact in person.contact_set.all():
                    OutboundMessage.objects.create(contact=contact, message=message)

        return message

    class Meta:
        model = Message