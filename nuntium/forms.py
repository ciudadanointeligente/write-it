from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple
from nuntium.models import Message, Instance
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
        self.instance = kwargs['instance']
        persons = Person.objects.filter(api_instance=self.instance.api_instance)
        self.fields['persons'].queryset = persons

    class Meta:
        model = Message