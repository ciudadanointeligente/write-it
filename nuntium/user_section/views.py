from django.contrib.auth.decorators import login_required
from subdomains.utils import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, DetailView, View, ListView
from django.views.generic.edit import UpdateView, DeleteView, FormView

from mailit.forms import MailitTemplateForm

from ..models import WriteItInstance, Message,\
    NewAnswerNotificationTemplate, ConfirmationTemplate, \
    Answer, WriteItInstanceConfig
from .forms import WriteItInstanceBasicForm, WriteItInstanceAdvancedUpdateForm, \
    NewAnswerNotificationTemplateForm, ConfirmationTemplateForm, \
    WriteItInstanceCreateForm, AnswerForm, \
    RelatePopitInstanceWithWriteItInstance
from django.contrib import messages as view_messages
from django.utils.translation import ugettext as _
import json


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
        context['people'] = self.object.persons.all()
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

        context['api_base_url'] = self.request.build_absolute_uri('/api/v1/')
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
    template_name_suffix = '_update_form'
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
            kwargs={'slug': self.object.slug},
            )


class WriteItInstanceAdvancedUpdateView(UpdateView):
    form_class = WriteItInstanceAdvancedUpdateForm
    template_name = 'nuntium/writeitinstance_advanced_update_form.html'
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

    def get_success_url(self):
        return reverse(
            'writeitinstance_advanced_update',
            kwargs={'slug': self.object.writeitinstance.slug},
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
    template_name = 'nuntium/profiles/your-instances.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WriteItInstanceCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(
            'writeitinstance_basic_update',
            subdomain=self.object.slug
            )

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        url = reverse('your-instances')
        return redirect(url)


class YourInstancesView(UserSectionListView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/your-instances.html'

    def get_context_data(self, **kwargs):
        kwargs = super(YourInstancesView, self).get_context_data(**kwargs)
        kwargs['new_instance_form'] = WriteItInstanceCreateForm()
        return kwargs


class LoginRequiredMixin(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class WriteItInstanceOwnerMixin(LoginRequiredMixin):
    def get_object(self):
        slug = self.kwargs.pop('slug')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, writeitinstance__slug=slug, writeitinstance__owner=self.request.user, pk=pk)


# Note that there is no need for subclasses of this to also subclass WriteItInstanceOwnerMixin
# as it does its own owner checking.
class UpdateTemplateWithWriteitBase(LoginRequiredMixin, UpdateView):
    def get_object(self):
        slug = self.kwargs.pop('slug')
        return get_object_or_404(self.model, writeitinstance__slug=slug, writeitinstance__owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(UpdateTemplateWithWriteitBase, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.object.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse(
            'writeitinstance_template_update',
            kwargs={'slug': self.object.writeitinstance.slug},
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


class MessageDelete(WriteItInstanceOwnerMixin, DeleteView):
    model = Message
    template_name = "nuntium/profiles/message_delete_confirm.html"

    def get_success_url(self):
        success_url = reverse(
            'messages_per_writeitinstance',
            kwargs={'slug': self.object.writeitinstance.slug},
            )
        return success_url


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
            kwargs={'slug': self.message.writeitinstance.slug, 'pk': self.message.pk},
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


class AcceptMessageView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.message = get_object_or_404(Message, id=kwargs['pk'])
        if self.message.writeitinstance.owner != self.request.user:
            raise Http404
        return super(AcceptMessageView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.message.moderate()

        url = reverse(
            'messages_per_writeitinstance',
            kwargs={'slug': self.message.writeitinstance.slug},
            )
        return redirect(url)


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
        return reverse('writeitinstance_basic_update', kwargs={'slug': self.kwargs.get('slug')})

    def form_valid(self, form):
        form.relate()
        # It returns an AsyncResult http://celery.readthedocs.org/en/latest/reference/celery.result.html
        # that we could use for future information about this process
        view_messages.add_message(self.request, view_messages.INFO, _("We are now getting the people from popit"))
        return super(WriteitPopitRelatingView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(WriteitPopitRelatingView, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.writeitinstance
        context['relations'] = self.writeitinstance.writeitinstancepopitinstancerecord_set.all()
        return context


class WriteItDeleteView(DeleteView):
    model = WriteItInstance

    def get_object(self, queryset=None):
        obj = super(WriteItDeleteView, self).get_object(queryset=queryset)
        if not obj.owner == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        url = reverse('your-instances')
        return url
