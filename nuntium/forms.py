# coding=utf-8
from django.forms import ModelForm, ModelMultipleChoiceField, SelectMultiple, URLField
from .models import Message, WriteItInstance, Confirmation

from contactos.models import Contact
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from popit.models import Person
from haystack.forms import SearchForm
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class PersonSelectMultipleWidget(SelectMultiple):
    def render_option(self, selected_choices, option_value, option_label):
        person = Person.objects.get(id=option_value)
        contacts_exist = Contact.are_there_contacts_for(person)
        if not contacts_exist:
            option_label += u" *"
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(u' selected="selected"')
            # I copied this from the original SelectMultiple
            # but this lines of code is not being used currently
            # for this reason the following lines of code are comented
            # if not self.allow_multiple_selected:
            #     # Only allow for a single selection.
            #     selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html(u'<option value="{0}"{1}>{2}</option>',
                           option_value,
                           selected_html,
                           force_text(option_label))


class PersonMultipleChoiceField(ModelMultipleChoiceField):
    widget = PersonSelectMultipleWidget(attrs={'class': 'chosen-person-select form-control'})

    def label_from_instance(self, obj):
        return obj.name


class MessageCreateForm(ModelForm):
    persons = PersonMultipleChoiceField(queryset=Person.objects.none())

    def __init__(self, *args, **kwargs):
        try:
            writeitinstance = kwargs.pop("writeitinstance")
        except:
            raise ValidationError(_('Instance not present'))
        self.writeitinstance = writeitinstance
        persons = writeitinstance.persons.all()
        super(MessageCreateForm, self).__init__(*args, **kwargs)
        self.instance.writeitinstance = self.writeitinstance
        self.fields['persons'].queryset = persons

    def save(self, force_insert=False, force_update=False, commit=True):
        message = super(MessageCreateForm, self).save(commit=False)
        if commit:
            persons = self.cleaned_data['persons']
            message.persons = persons
            message.save()
        # I know I have to move the previous code

        ## It creates a confirmation, a confirmation is sent automatically
        ## when created
        Confirmation.objects.create(message=message)

        return message

    def clean(self):
        cleaned_data = super(MessageCreateForm, self).clean()

        if not self.writeitinstance.config.allow_messages_using_form:
            raise ValidationError("")
        return cleaned_data

    class Meta:
        model = Message
        exclude = ("writeitinstance", "status", "slug", "moderated", "confirmated", "public")


class MessageSearchForm(SearchForm):
    pass


class PerInstanceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance', None)
        super(PerInstanceSearchForm, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.filter(writeitinstance=self.writeitinstance.id)


class WriteItInstanceCreateFormPopitUrl(ModelForm):
    popit_url = URLField(
        label=_('Url of the popit instance api'),
        help_text=_("Example: http://popit.master.ciudadanointeligente.org/api/"),
        required=False,
        )

    class Meta:
        model = WriteItInstance
        fields = ('owner', 'name', 'popit_url',
            "notify_owner_when_new_answer",
            "autoconfirm_api_messages")

    def relate_with_people(self):
        if self.cleaned_data['popit_url']:
            self.instance.load_persons_from_a_popit_api(
                self.cleaned_data['popit_url']
                )

    def save(self, commit=True):
        instance = super(WriteItInstanceCreateFormPopitUrl, self)\
            .save(commit=commit)

        if commit:
            self.relate_with_people()

        return instance
