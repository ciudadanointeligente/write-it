# coding=utf-8
from django.forms import ModelForm, TextInput, Textarea, \
    CheckboxInput, NumberInput
from django.core import validators

from nuntium.models import WriteItInstance, \
    NewAnswerNotificationTemplate, \
    ConfirmationTemplate, Answer, WriteItInstanceConfig, \
    WriteitInstancePopitInstanceRecord

from django.forms import ValidationError, ModelChoiceField, Form, URLField

from django.utils.translation import ugettext as _
from popit.models import Person
from ..forms import WriteItInstanceCreateFormPopitUrl, PopitParsingFormMixin
from django.conf import settings
from nuntium.popit_api_instance import PopitApiInstance


class WriteItInstanceBasicForm(ModelForm):
    class Meta:
        model = WriteItInstance
        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('Write to the people in power. Get answers. Be heard.'),
                    }),
            }


class WriteItInstanceAnswerNotificationForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = [ 'notify_owner_when_new_answer' ]
        widgets = { 
            'notify_owner_when_new_answer': CheckboxInput(attrs={'class': 'form-control'}),
        }

class WriteItInstanceWebBasedForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = [ 'allow_messages_using_form' ]
        widgets = { 
            'allow_messages_using_form': CheckboxInput(attrs={'class': 'form-control'}),
        }

class WriteItInstanceModerationForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = [ 'moderation_needed_in_all_messages' ]
        widgets = { 
            'moderation_needed_in_all_messages': CheckboxInput(attrs={'class': 'form-control'}),
        }

class WriteItInstanceApiAutoconfirmForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = [ 'autoconfirm_api_messages' ]
        widgets = { 
            'autoconfirm_api_messages': CheckboxInput(attrs={'class': 'form-control'}),
        }

class WriteItInstanceMaxRecipientsForm(ModelForm):
    class Meta:
        model = WriteItInstanceConfig
        fields = [ 'maximum_recipients' ]
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
        fields = [ 'rate_limiter' ]
        widgets = { 'rate_limiter': NumberInput(attrs={'class': 'form-control', 'min': 0}) }

    def __init__(self, *args, **kwargs):
        super(WriteItInstanceRateLimiterForm, self).__init__(*args, **kwargs)
        self.fields['rate_limiter'].validators.append(validators.MinValueValidator(0))


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


class SimpleInstanceCreateFormPopitUrl(WriteItInstanceCreateFormPopitUrl):
    class Meta:
        model = WriteItInstance
        fields = ('owner', 'name', 'popit_url')


class WriteItInstanceCreateForm(WriteItInstanceCreateFormPopitUrl):
    class Meta:
        model = WriteItInstance
        fields = ('name', 'popit_url')
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        if 'owner' in kwargs:
            self.owner = kwargs.pop('owner')
        super(WriteItInstanceCreateForm, self).__init__(*args, **kwargs)
        self.fields['popit_url'].widget.attrs['class'] = 'form-control'
        self.fields['popit_url'].widget.attrs['required'] = True

    def save(self, commit=True):
        instance = super(WriteItInstanceCreateForm, self).save(commit=False)
        instance.owner = self.owner
        instance.save()
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
        label=_('PopIt URL'),
        help_text=_("Example: https://eduskunta.popit.mysociety.org/"),
        )

    def __init__(self, *args, **kwargs):
        self.writeitinstance = kwargs.pop('writeitinstance')
        super(RelatePopitInstanceWithWriteItInstance, self).__init__(*args, **kwargs)

    def relate(self):
        result = self.writeitinstance.load_persons_from_a_popit_api(
            self.cleaned_data['popit_url']
            )
        return result

    def clean(self, *args, **kwargs):
        cleaned_data = super(RelatePopitInstanceWithWriteItInstance, self).clean(*args, **kwargs)
        if self.writeitinstance.writeitinstancepopitinstancerecord_set.filter(popitapiinstance__url=cleaned_data.get('popit_url')):
            self.relate()
            raise ValidationError(_("You have already added this PopIt. But we will fetch the data from it again now."))
        return cleaned_data


class WriteItPopitUpdateForm(ModelForm):
    class Meta:
        model = WriteitInstancePopitInstanceRecord
        fields = ['periodicity', ]
