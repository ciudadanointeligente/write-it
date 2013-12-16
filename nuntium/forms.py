from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple, \
                        CharField, EmailField, SelectMultiple, TextInput, Textarea
from nuntium.models import Message, WriteItInstance, OutboundMessage, \
                            Confirmation, Membership, NewAnswerNotificationTemplate
from contactos.models import Contact
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from popit.models import Person
from haystack.forms import SearchForm

class PersonMultipleChoiceField(ModelMultipleChoiceField):
    widget = SelectMultiple(attrs={'class': 'chosen-person-select form-control'})

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
        self.instance.writeitinstance = self.writeitinstance
        self.fields['persons'].queryset = persons

    def save(self, force_insert=False, force_update=False, commit=True):
        message = super(MessageCreateForm, self).save(commit=False)
        if commit:
            persons = self.cleaned_data['persons']
            message.persons = persons
            message.save()
        #I know I have to move the previous code


        ## It creates a confirmation, a confirmation is sent automatically
        ## when created
        Confirmation.objects.create(message=message)


        return message

    def clean(self):
        cleaned_data = super(MessageCreateForm, self).clean()

        if not self.writeitinstance.allow_messages_using_form:
            raise ValidationError("")
        return cleaned_data

    class Meta:
        model = Message
        exclude = ("writeitinstance", "status", "slug", "moderated", "confirmated")


class MessageSearchForm(SearchForm):
    pass


class PerInstanceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance', None)
        super(PerInstanceSearchForm, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.filter(writeitinstance=self.writeitinstance.id)


class WriteItInstanceBasicForm(ModelForm):
    class Meta:
        model = WriteItInstance
        fields = ['name', 'persons']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'persons': SelectMultiple(attrs={'class': 'form-control chosen-person-select'}),
        }


class NewAnswerNotificationTemplateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance')
        super(NewAnswerNotificationTemplateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        template = super(NewAnswerNotificationTemplateForm, self).save(commit=False)
        template.writeitinstance = self.writeitinstance
        if commit:
            template.save()
        return template

    class Meta:
        model = NewAnswerNotificationTemplate
        fields = ['subject_template', 'template_html', 'template_text']

        widgets = {
            'subject_template': TextInput(attrs={'class': 'form-control'}),
            'template_html': Textarea(attrs={'class': 'form-control'}),
            'template_text': Textarea(attrs={'class': 'form-control'}),
        }
