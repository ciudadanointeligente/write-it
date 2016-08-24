# coding=utf-8
from urlparse import urlparse

from django.conf import settings
from django.core import validators
from django.forms import (
    CharField,
    CheckboxInput,
    Form,
    ModelChoiceField,
    ModelForm,
    NumberInput,
    TextInput,
    Textarea,
    URLField,
    ValidationError,
    ChoiceField,
    Select,
    )

from django.utils.translation import ugettext as _

from popolo.models import Person

from instance.models import (
    WriteItInstance,
    WriteItInstanceConfig,
    WriteitInstancePopitInstanceRecord,
)
from nuntium.models import (
    Answer,
    ConfirmationTemplate,
    NewAnswerNotificationTemplate,
    AnswerWebHook,
    default_confirmation_template_content_text,
    default_confirmation_template_subject,
    default_new_answer_content_template,
    default_new_answer_subject_template,
    )

from ..forms import (
    WriteItInstanceCreateFormPopitUrl,
    PopitParsingFormMixin,
    )


class WriteItInstanceBasicForm(ModelForm):
    language = ChoiceField(choices=settings.LANGUAGES, widget=Select(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        try:
            kwargs['initial']['language'] = kwargs['instance'].config.default_language
        except KeyError:
            pass
        super(WriteItInstanceBasicForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        ret = super(WriteItInstanceBasicForm, self).save(*args, **kwargs)
        ret.config.default_language = self.cleaned_data['language']
        ret.config.save()
        return ret

    class Meta:
        model = WriteItInstance
        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('Write to the people who represent you.'),
                    }),
            }


class WriteItInstanceAnswerNotificationForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = ['notify_owner_when_new_answer']
        widgets = {
            'notify_owner_when_new_answer': CheckboxInput(attrs={'class': 'form-control'}),
        }


class WriteItInstanceWebBasedForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = ['allow_messages_using_form']
        widgets = {
            'allow_messages_using_form': CheckboxInput(attrs={'class': 'form-control'}),
        }


class WriteItInstanceModerationForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = ['moderation_needed_in_all_messages']
        widgets = {
            'moderation_needed_in_all_messages': CheckboxInput(attrs={'class': 'form-control'}),
        }

    # Do not allow moderation to be turned off until the moderation queue is
    # empty to avoid any problems with old messages never being moderated
    def clean_moderation_needed_in_all_messages(self):
        moderation_on = self.cleaned_data['moderation_needed_in_all_messages']
        writeitinstance = self.instance.writeitinstance
        if not moderation_on and writeitinstance.messages_awaiting_moderation.count() > 0:
            raise ValidationError("Cannot turn off moderation while there are un-moderated messages")

        return moderation_on


class WriteItInstanceApiAutoconfirmForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = ['autoconfirm_api_messages']
        widgets = {
            'autoconfirm_api_messages': CheckboxInput(attrs={'class': 'form-control'}),
        }


class WriteItInstanceMaxRecipientsForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = ['maximum_recipients']
        widgets = {
            'maximum_recipients': NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(WriteItInstanceMaxRecipientsForm, self).__init__(*args, **kwargs)
        self.fields['maximum_recipients'].validators.append(validators.MinValueValidator(1))
        self.fields['maximum_recipients'].validators.append(validators.MaxValueValidator(settings.OVERALL_MAX_RECIPIENTS))


class WriteItInstanceRateLimiterForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = ['rate_limiter']
        widgets = {'rate_limiter': NumberInput(attrs={'class': 'form-control', 'min': 0})}

    def __init__(self, *args, **kwargs):
        super(WriteItInstanceRateLimiterForm, self).__init__(*args, **kwargs)
        self.fields['rate_limiter'].validators.append(validators.MinValueValidator(0))


class NewAnswerNotificationTemplateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance')
        super(NewAnswerNotificationTemplateForm, self).__init__(*args, **kwargs)
        self.initial['template_text'] = self.initial['template_text'] or default_new_answer_content_template
        self.initial['subject_template'] = self.initial['subject_template'] or default_new_answer_subject_template

    def save(self, commit=True):
        template = super(NewAnswerNotificationTemplateForm, self).save(commit=False)
        if self.cleaned_data['template_text'] == default_new_answer_content_template:
            self.cleaned_data['template_text'] = None
        if self.cleaned_data['subject_template'] == default_new_answer_subject_template:
            self.cleaned_data['subject_template'] = None

        template.writeitinstance = self.writeitinstance
        if commit:
            template.save()
        return template

    class Meta:
        model = NewAnswerNotificationTemplate
        fields = ['subject_template', 'template_text']

        widgets = {
            'subject_template': TextInput(attrs={'class': 'form-control'}),
            'template_text': Textarea(attrs={'class': 'form-control'}),
        }


class ConfirmationTemplateForm(ModelForm):
    class Meta:
        model = ConfirmationTemplate
        fields = ['subject', 'content_text']
        widgets = {
            'subject': TextInput(attrs={'class': 'form-control'}),
            'content_text': Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        if "writeitinstance" not in kwargs:
            raise ValidationError(_("WriteIt Instance not present"))
        self.writeitinstance = kwargs.pop("writeitinstance")
        super(ConfirmationTemplateForm, self).__init__(*args, **kwargs)
        self.initial['subject'] = self.initial['subject'] or default_confirmation_template_subject
        self.initial['content_text'] = self.initial['content_text'] or default_confirmation_template_content_text

    def save(self, commit=True):
        template = super(ConfirmationTemplateForm, self).save(commit=commit)
        if template.subject == default_confirmation_template_subject:
            template.subject = u''
        if template.content_text == default_confirmation_template_content_text:
            template.content_text = u''
        if commit:
            template.save()
        return template


class SimpleInstanceCreateFormPopitUrl(WriteItInstanceCreateFormPopitUrl):
    class Meta:
        model = WriteItInstance
        fields = ('owner', 'name', 'popit_url')


class WriteItInstanceCreateForm(WriteItInstanceCreateFormPopitUrl):
    slug = CharField(
        label=_("The subdomain your site will run at"),
        help_text=_("Choose wisely; this can't be changed."),
        required=True,
        min_length=4,
        )

    class Meta:
        model = WriteItInstance
        fields = ('popit_url', 'slug')

    def __init__(self, *args, **kwargs):
        if 'owner' in kwargs:
            self.owner = kwargs.pop('owner')
        super(WriteItInstanceCreateForm, self).__init__(*args, **kwargs)
        self.fields['popit_url'].widget.attrs['class'] = 'form-control'
        self.fields['popit_url'].widget.attrs['required'] = True
        self.fields['slug'].widget.attrs['class'] = 'form-control'

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            return slug
        url_validator = validators.URLValidator(message="Enter a valid subdomain")
        url = 'http://%s.example.com' % slug
        url_validator(url)
        slug_exists = WriteItInstance.objects.filter(slug__iexact=slug).exists()
        if slug_exists:
            raise ValidationError(_("This subdomain has already been taken."))
        return slug

    def save(self, commit=True):
        instance = super(WriteItInstanceCreateForm, self).save(commit=False)
        slug = self.cleaned_data['slug']
        instance.slug = slug
        instance.name = slug
        instance.owner = self.owner
        instance.save()
        instance.config.default_language = settings.LANGUAGE_CODE
        instance.config.save()
        self.relate_with_people()
        return instance


class AnswerForm(ModelForm):
    person = ModelChoiceField(queryset=Person.objects.none())

    class Meta:
        model = Answer
        fields = ('person', 'content')
        widgets = {
            'content': TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop('message')
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['person'].queryset = self.message.people
        self.fields['person'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        answer = super(AnswerForm, self).save(commit=False)
        answer.message = self.message
        answer.save()
        return answer


class RelatePopitInstanceWithWriteItInstance(Form, PopitParsingFormMixin):
    popit_url = URLField(
        label=_('Popolo URL'),
        help_text=_("Example: https://cdn.rawgit.com/everypolitician/everypolitician-data/1460373/data/Abkhazia/Assembly/ep-popolo-v1.0.json"),
        )

    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance')
        super(RelatePopitInstanceWithWriteItInstance, self).__init__(*args, **kwargs)

    def relate(self):
        result = self.writeitinstance.load_persons_from_popolo_json(
            self.cleaned_data['popit_url']
            )
        return result

    def clean(self, *args, **kwargs):
        cleaned_data = super(RelatePopitInstanceWithWriteItInstance, self).clean(*args, **kwargs)
        if self.writeitinstance.writeitinstancepopitinstancerecord_set.filter(popolo_source__url=cleaned_data.get('popit_url')):
            self.relate()
            raise ValidationError(_("You have already added this source. But we will fetch the data from it again now."))
        return cleaned_data


class WriteItPopitUpdateForm(ModelForm):
    class Meta:
        model = WriteitInstancePopitInstanceRecord
        fields = ['periodicity']


class WebhookCreateForm(ModelForm):
    class Meta:
        model = AnswerWebHook
        fields = ['url']

    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance')
        super(WebhookCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        webhook = super(WebhookCreateForm, self).save(commit=False)
        webhook.writeitinstance = self.writeitinstance
        webhook.save()
        return webhook
