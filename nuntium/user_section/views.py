import requests

from django.contrib.auth.decorators import login_required
from subdomains.utils import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, DetailView, View, ListView, RedirectView
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.core.exceptions import ValidationError

from mailit.forms import MailitTemplateForm

from instance.models import WriteItInstance, WriteItInstanceConfig, WriteitInstancePopitInstanceRecord
from popolo_sources.models import PopoloSource
from ..models import Message,\
    NewAnswerNotificationTemplate, ConfirmationTemplate, \
    Answer, Moderation, \
    AnswerWebHook
from .forms import WriteItInstanceBasicForm, \
    NewAnswerNotificationTemplateForm, ConfirmationTemplateForm, \
    WriteItInstanceAnswerNotificationForm, \
    WriteItInstanceApiAutoconfirmForm, \
    WriteItInstanceCreateForm, \
    WriteItInstanceModerationForm, \
    WriteItInstanceMaxRecipientsForm, \
    WriteItInstanceRateLimiterForm, \
    WriteItInstanceWebBasedForm, \
    AnswerForm, RelatePopitInstanceWithWriteItInstance, \
    WebhookCreateForm
from django.contrib import messages as view_messages
from django.utils.translation import ugettext as _
import json
from nuntium.tasks import pull_from_popolo_json
from nuntium.user_section.forms import WriteItPopitUpdateForm
from django.contrib.sites.models import Site


class UserAccountView(TemplateView):
    template_name = 'nuntium/profiles/your-profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserAccountView, self).dispatch(*args, **kwargs)


class WriteItInstanceDetailBaseView(DetailView):
    model = WriteItInstance

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.object = super(DetailView, self).get_object(queryset=queryset)
        #OK I don't know if it is better to test by id
        if not self.object.owner.__eq__(self.request.user):
            raise Http404
        return self.object


class WriteItInstanceContactDetailView(WriteItInstanceDetailBaseView):
    template_name = 'nuntium/profiles/contacts/contacts-per-writeitinstance.html'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WriteItInstanceContactDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceContactDetailView, self).get_context_data(**kwargs)
        context['people'] = self.object.persons.order_by('name')
        return context


class WriteItInstanceStatusView(WriteItInstanceDetailBaseView):
    def render_to_response(self, context, **response_kwargs):
        status = self.object.pulling_from_popit_status
        return HttpResponse(
            json.dumps(status),
            content_type='application/json',
            **response_kwargs
        )


class WriteItInstanceApiDocsView(WriteItInstanceDetailBaseView):
    template_name = 'nuntium/writeitinstance_api_docs.html'

    def get_context_data(self, *args, **kwargs):
        context = super(WriteItInstanceApiDocsView, self).get_context_data(*args, **kwargs)
        current_domain = Site.objects.get_current().domain
        context['api_base_url'] = 'http://' + current_domain + '/api/v1/'
        return context


class WriteItInstanceTemplateUpdateView(DetailView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/templates.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WriteItInstanceTemplateUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.object = super(WriteItInstanceTemplateUpdateView, self).get_object(queryset=queryset)
        #OK I don't know if it is better to test by id
        if not self.object.owner.__eq__(self.request.user):
            raise Http404
        return self.object

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceTemplateUpdateView, self).get_context_data(**kwargs)
        context['new_answer_template_form'] = NewAnswerNotificationTemplateForm(
            writeitinstance=self.object,
            instance=self.object.new_answer_notification_template,
            )

        context['mailit_template_form'] = MailitTemplateForm(
            writeitinstance=self.object,
            instance=self.object.mailit_template,
            )
        context['confirmation_template_form'] = ConfirmationTemplateForm(
            writeitinstance=self.object,
            instance=self.object.confirmationtemplate,
            )
        return context


class WriteItInstanceUpdateView(UpdateView):
    form_class = WriteItInstanceBasicForm
    template_name = "nuntium/writeitinstance_update_form.html"
    model = WriteItInstance

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WriteItInstanceUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(WriteItInstanceUpdateView, self).get_queryset().filter(owner=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse(
            'writeitinstance_basic_update',
            subdomain=self.object.slug,
            )


class WriteItInstanceAdvancedUpdateView(UpdateView):
    model = WriteItInstanceConfig

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WriteItInstanceAdvancedUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super(WriteItInstanceAdvancedUpdateView, self).get_queryset().filter(writeitinstance__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceAdvancedUpdateView, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.object.writeitinstance
        return context

    def get_slug_field(self):
        return 'writeitinstance__slug'


class WriteItInstanceAnswerNotificationView(WriteItInstanceAdvancedUpdateView):
    form_class = WriteItInstanceAnswerNotificationForm
    template_name = 'nuntium/writeitinstance_answernotification_form.html'

    def get_success_url(self):
        return reverse(
            'writeitinstance_answernotification_update',
            subdomain=self.object.writeitinstance.slug
            )


class WriteItInstanceRateLimiterView(WriteItInstanceAdvancedUpdateView):
    form_class = WriteItInstanceRateLimiterForm
    template_name = 'nuntium/writeitinstance_ratelimiter_form.html'

    def get_success_url(self):
        return reverse(
            'writeitinstance_ratelimiter_update',
            subdomain=self.object.writeitinstance.slug
            )


class WriteItInstanceModerationView(WriteItInstanceAdvancedUpdateView):
    form_class = WriteItInstanceModerationForm
    template_name = 'nuntium/writeitinstance_moderation_form.html'

    def get_success_url(self):
        return reverse(
            'writeitinstance_moderation_update',
            subdomain=self.object.writeitinstance.slug
            )


class WriteItInstanceApiAutoconfirmView(WriteItInstanceAdvancedUpdateView):
    form_class = WriteItInstanceApiAutoconfirmForm
    template_name = 'nuntium/writeitinstance_autoconfirm_form.html'

    def get_success_url(self):
        return reverse(
            'writeitinstance_api_autoconfirm_update',
            subdomain=self.object.writeitinstance.slug
            )


class WriteItInstanceMaxRecipientsView(WriteItInstanceAdvancedUpdateView):
    form_class = WriteItInstanceMaxRecipientsForm
    template_name = 'nuntium/writeitinstance_max_recipients_form.html'

    def get_success_url(self):
        return reverse(
            'writeitinstance_maxrecipients_update',
            subdomain=self.object.writeitinstance.slug
            )


class WriteItInstanceWebBasedView(WriteItInstanceAdvancedUpdateView):
    form_class = WriteItInstanceWebBasedForm
    template_name = 'nuntium/writeitinstance_web_based_form.html'

    def get_success_url(self):
        return reverse(
            'writeitinstance_webbased_update',
            subdomain=self.object.writeitinstance.slug
            )


class UserSectionListView(ListView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserSectionListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super(UserSectionListView, self).get_queryset().filter(owner=self.request.user)
        return queryset


class WriteItInstanceCreateView(CreateView):
    model = WriteItInstance
    form_class = WriteItInstanceCreateForm
    template_name = 'nuntium/create_new_writeitinstance.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WriteItInstanceCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(
            'welcome',
            subdomain=self.object.slug
            )

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        if 'data' in kwargs and kwargs['data'].get('legislature'):
            kwargs['data'] = kwargs['data'].copy()
            kwargs['data']['popit_url'] = kwargs['data']['legislature']
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(WriteItInstanceCreateView, self).get_context_data(*args, **kwargs)
        countries_json_url = ('http://everypolitician.github.io/'
            'everypolitician-writeinpublic/countries.json')
        context['countries'] = requests.get(countries_json_url).json()
        return context


class YourInstancesView(UserSectionListView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/your-instances.html'

    def get_context_data(self, **kwargs):
        kwargs = super(YourInstancesView, self).get_context_data(**kwargs)
        kwargs['new_instance_form'] = WriteItInstanceCreateForm()
        kwargs['live_sites'] = kwargs['object_list'].filter(config__testing_mode=False)
        kwargs['test_sites'] = kwargs['object_list'].filter(config__testing_mode=True)
        return kwargs


class LoginRequiredMixin(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class WriteItInstanceOwnerMixin(LoginRequiredMixin):
    def get_object(self):
        slug = self.request.subdomain
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, writeitinstance__slug=slug, writeitinstance__owner=self.request.user, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceOwnerMixin, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.object.writeitinstance
        return context


# Note that there is no need for subclasses of this to also subclass WriteItInstanceOwnerMixin
# as it does its own owner checking.
class UpdateTemplateWithWriteitBase(LoginRequiredMixin, UpdateView):
    def get_object(self):
        return get_object_or_404(self.model, writeitinstance__slug=self.request.subdomain, writeitinstance__owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(UpdateTemplateWithWriteitBase, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.object.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse(
            'writeitinstance_template_update',
            subdomain=self.object.writeitinstance.slug,
            )


class NewAnswerNotificationTemplateUpdateView(UpdateTemplateWithWriteitBase):
    form_class = NewAnswerNotificationTemplateForm
    model = NewAnswerNotificationTemplate


class ConfirmationTemplateUpdateView(UpdateTemplateWithWriteitBase):
    form_class = ConfirmationTemplateForm
    model = ConfirmationTemplate


class MessagesPerWriteItInstance(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'nuntium/profiles/messages_per_instance.html'

    def get_queryset(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=self.request.subdomain, owner=self.request.user)
        return super(MessagesPerWriteItInstance, self).get_queryset().filter(writeitinstance=self.writeitinstance)

    def get_context_data(self, **kwargs):
        context = super(MessagesPerWriteItInstance, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.writeitinstance
        return context


class MessageDetail(WriteItInstanceOwnerMixin, DetailView):
    model = Message
    template_name = "nuntium/profiles/message_detail.html"


class AnswerEditMixin(View):
    def get_message(self):
        raise NotImplementedError

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.message = self.get_message()
        if self.message.writeitinstance.owner != self.request.user:
            raise Http404
        return super(AnswerEditMixin, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(
            'message_detail_private',
            subdomain=self.message.writeitinstance.slug,
            kwargs={'pk': self.message.pk},
            )


class AnswerCreateView(AnswerEditMixin, CreateView):
    model = Answer
    template_name = "nuntium/profiles/create_answer.html"
    form_class = AnswerForm

    def get_message(self):
        message = Message.objects.get(id=self.kwargs['pk'])
        return message

    def get_form_kwargs(self):
        kwargs = super(AnswerCreateView, self).get_form_kwargs()
        kwargs['message'] = self.message
        return kwargs


class AnswerUpdateView(AnswerEditMixin, UpdateView):
    model = Answer
    template_name = "nuntium/profiles/update_answer.html"
    fields = ['content']

    def get_message(self):
        return self.model.objects.get(id=self.kwargs['pk']).message


class AcceptMessageView(RedirectView):
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AcceptMessageView, self).dispatch(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        message = get_object_or_404(Message,
            pk=kwargs['pk'],
            writeitinstance__slug=self.request.subdomain,
            writeitinstance__owner=self.request.user
            )
        message.moderate()
        view_messages.info(self.request, _('The message "%(message)s" has been accepted') % {'message': message})
        return reverse(
            'messages_per_writeitinstance',
            subdomain=message.writeitinstance.slug,
            )


class RejectMessageView(RedirectView):
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RejectMessageView, self).dispatch(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        message = get_object_or_404(Message,
            pk=kwargs['pk'],
            writeitinstance__slug=self.request.subdomain,
            writeitinstance__owner=self.request.user
            )
        if message.moderated:
            raise ValidationError(_('Cannot moderate an already moderated message'))
        message.public = False
        message.moderated = True
        message.save()
        view_messages.info(self.request, _('The message "%(message)s" has been rejected') % {'message': message})
        return reverse(
            'messages_per_writeitinstance',
            subdomain=message.writeitinstance.slug,
            )


class ModerationView(DetailView):
    model = Moderation
    slug_field = 'key'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModerationView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super(ModerationView, self).get_queryset()
        queryset.filter(
            message__writeitinstance__owner=self.request.user,
            message__writeitinstance__slug=self.request.subdomain,
        )
        return queryset


class AcceptModerationView(ModerationView):
    template_name = "nuntium/moderation_accepted.html"

    def get(self, *args, **kwargs):
        moderation = self.get_object()
        moderation.message.moderate()
        return super(AcceptModerationView, self).get(*args, **kwargs)


class RejectModerationView(ModerationView):
    template_name = "nuntium/moderation_rejected.html"

    def get(self, *args, **kwargs):
        get = super(RejectModerationView, self).get(*args, **kwargs)
        if self.object.message.moderated:
            raise ValidationError(_('Cannot moderate an already moderated message'))
        self.object.message.public = False
        # It is turned True to avoid users to
        # mistakenly moderate this message
        # in the admin section
        self.object.message.moderated = True
        self.object.message.save()
        return get


class ModerationQueue(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'nuntium/profiles/moderation_queue.html'

    def get_queryset(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=self.request.subdomain, owner=self.request.user)
        return Message.moderation_required_objects.filter(writeitinstance=self.writeitinstance)

    def get_context_data(self, **kwargs):
        context = super(ModerationQueue, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.writeitinstance
        return context


class WriteitPopitRelatingView(FormView):
    form_class = RelatePopitInstanceWithWriteItInstance
    template_name = 'nuntium/profiles/writeitinstance_and_popit_relations.html'

    # This method also checks for instance ownership
    def get_writeitinstance(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=self.request.subdomain, owner=self.request.user)

    def dispatch(self, *args, **kwargs):
        self.get_writeitinstance()
        return super(WriteitPopitRelatingView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(WriteitPopitRelatingView, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse('relate-writeit-popit', subdomain=self.writeitinstance.slug)

    def form_valid(self, form):
        form.relate()
        # It returns an AsyncResult http://celery.readthedocs.org/en/latest/reference/celery.result.html
        # that we could use for future information about this process
        return super(WriteitPopitRelatingView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(WriteitPopitRelatingView, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.writeitinstance
        context['relations'] = self.writeitinstance.writeitinstancepopitinstancerecord_set.all()
        return context


class ReSyncFromPopit(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            raise Http404
        return super(ReSyncFromPopit, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        writeitinstance = get_object_or_404(WriteItInstance,
            slug=self.request.subdomain,
            owner=self.request.user)
        popolo_sources_previously_related = PopoloSource.objects.filter(
            writeitinstancepopitinstancerecord__writeitinstance=writeitinstance)

        popolo_source = get_object_or_404(
            popolo_sources_previously_related,
            pk=kwargs['popolo_source_pk'])
        pull_from_popolo_json.delay(writeitinstance, popolo_source)
        return HttpResponse()


class WriteItPopitUpdateView(UpdateView):
    form_class = WriteItPopitUpdateForm
    model = WriteitInstancePopitInstanceRecord

    def get_writeitinstance(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=self.request.subdomain, owner=self.request.user)

    def dispatch(self, *args, **kwargs):
        self.get_writeitinstance()
        if self.request.method != 'POST':
            return self.http_method_not_allowed(*args, **kwargs)
        return super(WriteItPopitUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponse(
            json.dumps({
                'id': form.instance.id,
                'periodicity': form.instance.periodicity
                }),
            content_type='application/json'
        )

    def form_invalid(self, form):
        super(WriteItPopitUpdateView, self).form_invalid(form)
        return HttpResponse(
            json.dumps({
                'errors': form.errors
                }),
            content_type='application/json'
        )


class WriteItDeleteView(DeleteView):
    model = WriteItInstance

    # @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WriteItDeleteView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(WriteItDeleteView, self).get_object(queryset=queryset)
        if not obj.owner == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        url = reverse('your-instances')
        return url


class MessageTogglePublic(RedirectView):
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageTogglePublic, self).dispatch(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        message = get_object_or_404(Message,
            pk=kwargs['pk'],
            writeitinstance__slug=self.request.subdomain,
            writeitinstance__owner=self.request.user,
            )
        message.public = not message.public
        message.save()
        if message.public:
            view_messages.info(self.request, _("This message has been marked as public"))
        else:
            view_messages.info(self.request, _("This message has been marked as private"))
        return reverse('messages_per_writeitinstance', subdomain=self.request.subdomain)


class ContactUsView(TemplateView):
    template_name = 'nuntium/profiles/contact.html'


class WelcomeView(DetailView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/welcome.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WelcomeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WelcomeView, self).get_context_data(**kwargs)
        # passing URLs in for easy insertion into the translation tags
        # because we're using an overridden version of the url tag that
        # doesn't allow the use of "as" to pass the url as a variable
        # that can be quoted within a translation block. *sigh*
        context['url_template_update'] = reverse('writeitinstance_template_update', subdomain=self.request.subdomain)
        context['url_basic_update'] = reverse('writeitinstance_basic_update', subdomain=self.request.subdomain)
        context['url_maxrecipients_update'] = reverse('writeitinstance_maxrecipients_update', subdomain=self.request.subdomain)
        context['url_answernotification_update'] = reverse('writeitinstance_answernotification_update', subdomain=self.request.subdomain)
        context['url_recipients'] = reverse('contacts-per-writeitinstance', subdomain=self.request.subdomain)
        context['url_data_sources'] = reverse('relate-writeit-popit', subdomain=self.request.subdomain)
        return context


class WriteItInstanceWebHooksView(WriteItInstanceDetailBaseView):
    template_name = 'nuntium/profiles/webhooks.html'

    def get_context_data(self, *args, **kwargs):
        context = super(WriteItInstanceWebHooksView, self).get_context_data(*args, **kwargs)
        context['form'] = WebhookCreateForm(writeitinstance=self.object)
        return context


class WriteItInstanceCreateWebHooksView(CreateView):
    model = AnswerWebHook
    form_class = WebhookCreateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        self.writeitinstance = get_object_or_404(WriteItInstance,
            slug=self.kwargs['slug'],
            owner=self.request.user)
        return super(WriteItInstanceCreateWebHooksView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceCreateWebHooksView, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse(
            'writeitinstance_webhooks',
            subdomain=self.writeitinstance.slug,
            )
