from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple
from nuntium.models import Message, Contact, Instance
from django.forms import ValidationError
from django.utils.translation import ugettext as _

class MessageCreateForm(ModelForm):
    ''' docstring for MessageCreateForm'''
    contacts = ModelMultipleChoiceField(queryset=Contact.objects.all(), \
                                        widget=CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        if len(args)>0 and 'instance' in args[0]:
            instance_id = args[0]['instance']

            kwargs['instance'] = Instance.objects.get(id=instance_id)

        if 'instance' not in kwargs:
            raise ValidationError(_('Instance not present'))
        self.instance = kwargs['instance']
        return super(MessageCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Message