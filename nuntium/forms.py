# coding=utf-8
import urlparse

from django.forms import ModelForm, ModelMultipleChoiceField, SelectMultiple, URLField, Form, Textarea, TextInput, EmailInput
from contactos.models import Contact
from instance.models import WriteItInstance
from .models import Message, Confirmation

from popolo.models import Person
from django.forms import ValidationError
from django.utils.translation import ugettext as _, ungettext, pgettext_lazy
from haystack.forms import SearchForm
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class PersonSelectMultipleWidget(SelectMultiple):

    def __init__(self, *args, **kwargs):
        person_queryset = kwargs.pop('person_queryset')
        self.include_area_names = kwargs.pop('include_area_names')
        super(PersonSelectMultipleWidget, self).__init__(*args, **kwargs)
        self.person_id_to_person = {
            person.id: person
            for person in person_queryset
        }

    def render_option(self, selected_choices, option_value, option_label):
        person = self.person_id_to_person[option_value]
        if self.include_area_names:
            # See if we can find an area to append to the name:
            most_recent_membership = None
            for m in person.memberships.all():
                most_recent_membership = m
            if most_recent_membership and most_recent_membership.area:
                area_name = most_recent_membership.area.name
                option_label = u'{name} ({area_name})'.format(
                    name=option_label,
                    area_name=area_name,
                )
        css_class = 'uncontactable'
        for contact in person.contact_set.all():
            if not contact.is_bounced:
                css_class = ''
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
        return format_html(u'<option class="{0}" value="{1}"{2}>{3}</option>',
                           css_class,
                           option_value,
                           selected_html,
                           force_text(option_label))


class PersonMultipleChoiceField(ModelMultipleChoiceField):

    def __init__(self, queryset, include_area_names, *args, **kwargs):
        kwargs['widget'] = PersonSelectMultipleWidget(
            person_queryset=queryset,
            include_area_names=include_area_names,
            attrs={'class': 'chosen-person-select'}
        )
        super(PersonMultipleChoiceField, self).__init__(
            queryset, *args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class MessageCreateForm(ModelForm):
    persons = PersonMultipleChoiceField(
        queryset=Person.objects.none(), include_area_names=False)

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
        if len(cleaned_data['persons']) > self.writeitinstance.config.maximum_recipients:
            error_messages = ungettext(
                'You can send messages to at most %(count)d person',
                'You can send messages to at most %(count)d people',
                self.writeitinstance.config.maximum_recipients) % {
                'count': self.writeitinstance.config.maximum_recipients,
            }
            raise ValidationError(error_messages)
        return cleaned_data

    class Meta:
        model = Message
        exclude = ("writeitinstance", "status", "slug", "moderated", "confirmated", "public")


class WhoForm(Form):

    def __init__(self, persons_queryset, include_area_names, *args, **kwargs):
        super(WhoForm, self).__init__(*args, **kwargs)
        self.fields['persons'] = \
            PersonMultipleChoiceField(
                queryset=persons_queryset, include_area_names=include_area_names)

    def clean_persons(self):
        data = self.cleaned_data['persons']
        non_contactable_persons = [
            p.name for p in data
            if not p.contact_set.filter(is_bounced=False).exists()
        ]
        if non_contactable_persons:
            msg = _("We have no contact details for the following "
                    "people: {list_of_names}")
            raise ValidationError(msg.format(
                list_of_names=", ".join(non_contactable_persons)))
        return data


class DraftForm(ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'subject', 'author_name', 'author_email']
        widgets = {
            'content': Textarea(attrs={
                'class': 'form-control',
                'required': 'True'
            }),
            'subject': TextInput(attrs={
                'class': 'form-control',
                'required': 'True'
            }),
            'author_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': pgettext_lazy(
                    "An example author name when drafting a message",
                    "Alice Smith"
                )
            }),
            'author_email': EmailInput(attrs={
                'class': 'form-control',
                'required': 'True',
                'placeholder': pgettext_lazy(
                    "An example email address when drafting a message",
                    "alice@example.com"
                )
            }),
        }

    def __init__(self, allow_anonymous_messages, *args, **kwargs):
        super(DraftForm, self).__init__(*args, **kwargs)
        self.allow_anonymous_messages = allow_anonymous_messages

    def clean_author_name(self):
        if not self.allow_anonymous_messages and self.cleaned_data['author_name'] == '':
            raise ValidationError(_('Author name is required'), code='name_required')
        return self.cleaned_data['author_name']


class PreviewForm(ModelForm):
    class Meta:
        model = Message
        fields = []


class MessageSearchForm(SearchForm):
    pass


class PerInstanceSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance', None)
        super(PerInstanceSearchForm, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.filter(writeitinstance=self.writeitinstance.id)


class PopitParsingFormMixin(object):
    def get_scheme(self, hostname, scheme):
        if 'popit.mysociety.org' in hostname:
            return 'https'
        else:
            return scheme

    def get_path(self, hostname, path):
        if 'popit.mysociety.org' in hostname:
            return '/api/v0.1'
        else:
            return path

    def get_popit_url_parsed(self, popit_url):
        url = urlparse.urlparse(popit_url)
        popit_url = urlparse.urlunparse((
            self.get_scheme(url.netloc, url.scheme),
            url.netloc,
            self.get_path(url.netloc, url.path),
            url.params,
            url.query,
            url.fragment
        ))
        return popit_url

    def clean_popit_url(self):
        popit_url = self.cleaned_data.get('popit_url')
        return self.get_popit_url_parsed(popit_url)


class WriteItInstanceCreateFormPopitUrl(ModelForm, PopitParsingFormMixin):
    popit_url = URLField(
        label=_('Popolo URL'),
        help_text=_("Example: https://cdn.rawgit.com/everypolitician/everypolitician-data/1460373/data/Abkhazia/Assembly/ep-popolo-v1.0.json"),
        required=True,
        )

    class Meta:
        model = WriteItInstance
        fields = ('owner', 'name', 'popit_url')

    def relate_with_people(self):
        if self.cleaned_data['popit_url']:
            popit_url = self.cleaned_data['popit_url']
            self.instance.load_persons_from_popolo_json(
                popit_url
                )

    def save(self, commit=True):
        instance = super(WriteItInstanceCreateFormPopitUrl, self)\
            .save(commit=commit)

        if commit:
            self.relate_with_people()

        return instance
