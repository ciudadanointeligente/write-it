from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple, CharField, EmailField
from nuntium.models import Message, WriteItInstance, OutboundMessage, Confirmation
from contactos.models import Contact
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from popit.models import Person
from haystack.forms import SearchForm

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
        persons = Person.objects.filter(writeit_instances=writeitinstance)
        super(MessageCreateForm, self).__init__(*args, **kwargs)
        self.fields['persons'].queryset = persons

    def save(self, force_insert=False, force_update=False, commit=True):
        message = super(MessageCreateForm, self).save(commit=False)
        message.writeitinstance = self.writeitinstance
        if commit:
            persons = self.cleaned_data['persons']
            message.persons = persons
            message.save()
        #I know I have to move the previous code


        ## It creates a confirmation, a confirmation is sent automatically
        ## when created
        Confirmation.objects.create(message=message)


        return message

    class Meta:
        model = Message
        exclude = ("writeitinstance", "status", "slug")


class MessageSearchForm(SearchForm):
    pass


class PerInstanceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance', None)
        super(PerInstanceSearchForm, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.filter(writeitinstance=self.writeitinstance.id)