from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, DetailView, View, ListView
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin

from contactos.models import Contact
from mailit.forms import MailitTemplateForm

from ..models import WriteItInstance, Message,\
    NewAnswerNotificationTemplate, ConfirmationTemplate, \
    WriteitInstancePopitInstanceRecord, Answer, WriteItInstanceConfig
from .forms import WriteItInstanceBasicForm, WriteItInstanceAdvancedUpdateForm, \
    NewAnswerNotificationTemplateForm, ConfirmationTemplateForm, \
    WriteItInstanceCreateForm, AnswerForm, \
    RelatePopitInstanceWithWriteItInstance
from nuntium.popit_api_instance import PopitApiInstance
from django.contrib import messages as view_messages
from django.utils.translation import ugettext as _
import json


class UserAccountView(TemplateView):
    template_name = 'nuntium/profiles/your-profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserAccountView, self).dispatch(*args, **kwargs)


class WriteItInstanceDetailMixin(DetailView):
    model = WriteItInstance

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DetailView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        self.object = super(DetailView, self).get_object(queryset=queryset)
        #OK I don't know if it is better to test by id
        if not self.object.owner.__eq__(self.request.user):
            raise Http404
        return self.object


class WriteItInstanceContactDetailView(WriteItInstanceDetailMixin):
    template_name = 'nuntium/profiles/contacts/contacts-per-writeitinstance.html'

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceContactDetailView, self).get_context_data(**kwargs)
        context['people'] = self.object.persons.all()
        return context


class WriteItInstanceStatusView(WriteItInstanceDetailMixin):
    def render_to_response(self, context, **response_kwargs):
        status = self.object.pulling_from_popit_status
        return HttpResponse(
            json.dumps(status),
            content_type='application/json',
            **response_kwargs
        )


class WriteItInstanceTemplateUpdateView(DetailView):
    model = WriteItInstance
    template_name = 'nuntium/profiles/templates.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WriteItInstanceTemplateUpdateView, self).dispatch(*args, **kwargs)

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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = WriteItInstance.objects.filter(owner=self.request.user)
        return super(WriteItInstanceUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(
            'writeitinstance_basic_update',
            kwargs={'pk': self.object.pk},
            )


class WriteItInstanceAdvancedUpdateView(UpdateView):
    form_class = WriteItInstanceAdvancedUpdateForm
    template_name = 'nuntium/writeitinstance_advanced_update_form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.queryset = WriteItInstanceConfig.objects.filter(writeitinstance__owner=self.request.user)
        return super(WriteItInstanceAdvancedUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceAdvancedUpdateView, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.object.writeitinstance
        return context

    def get_success_url(self):
        return reverse(
            'writeitinstance_advanced_update',
            kwargs={'pk': self.object.pk},
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
            kwargs={'pk': self.object.pk},
            )

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        url = reverse('your-instances')
        return redirect(url)


class YourContactsView(UserSectionListView):
    model = Contact
    template_name = 'nuntium/profiles/your-contacts.html'

    def get_queryset(self):
        queryset = Contact.objects.filter(writeitinstance__owner=self.request.user)
        return queryset


class YourPopitApiInstances(ListView):
    model = WriteitInstancePopitInstanceRecord
    template_name = 'nuntium/profiles/your-popit-apis.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(YourPopitApiInstances, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super(YourPopitApiInstances, self).get_queryset()
        queryset = queryset.filter(writeitinstance__owner=self.request.user)
        return queryset


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


class WriteItInstanceOwnerMixin(SingleObjectMixin):
    def get_writeitinstance(self):
        return get_object_or_404(WriteItInstance, pk=self.kwargs['pk'])

    def check_ownership(self):
        self.writeitinstance = self.get_writeitinstance()
        if not self.writeitinstance.owner.__eq__(self.request.user):
            raise Http404

    def get_object(self):
        self.check_ownership()
        self.object = super(WriteItInstanceOwnerMixin, self).get_object()
        return self.object


class WriteItRelatedModelMixin(SingleObjectMixin):
    def get_writeitinstance(self):
        obj = get_object_or_404(self.model, writeitinstance__pk=self.kwargs['pk'])
        return obj.writeitinstance


class UpdateTemplateWithWriteitMixin(WriteItRelatedModelMixin, UpdateView, LoginRequiredMixin, WriteItInstanceOwnerMixin):
    def get_object(self):
        self.check_ownership()
        self.object = self.model.objects.get(writeitinstance=self.writeitinstance)
        return self.object

    def get_form_kwargs(self):
        kwargs = super(UpdateTemplateWithWriteitMixin, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse(
            'writeitinstance_template_update',
            kwargs={'pk': self.writeitinstance.pk},
            )


class NewAnswerNotificationTemplateUpdateView(UpdateTemplateWithWriteitMixin):
    form_class = NewAnswerNotificationTemplateForm
    model = NewAnswerNotificationTemplate


class ConfirmationTemplateUpdateView(UpdateTemplateWithWriteitMixin):
    form_class = ConfirmationTemplateForm
    model = ConfirmationTemplate


class WriteItPopitUpdateView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WriteItPopitUpdateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        record = WriteitInstancePopitInstanceRecord.objects.get(id=kwargs.get('pk'))
        if record.writeitinstance.owner != request.user:
            return HttpResponseForbidden()
        popit_api_instance = PopitApiInstance.objects.get(id=record.popitapiinstance.id)
        record.writeitinstance.\
            relate_with_persons_from_popit_api_instance(popit_api_instance)
        return HttpResponse('result')


class MessagesPerWriteItInstance(DetailView, LoginRequiredMixin, WriteItInstanceOwnerMixin):
    model = WriteItInstance
    template_name = 'nuntium/profiles/messages_per_instance.html'

    def get_context_data(self, **kwargs):
        context = super(MessagesPerWriteItInstance, self).get_context_data(**kwargs)
        context['writeit_messages'] = self.object.message_set.all()
        return context


class MessageDetail(WriteItRelatedModelMixin, DetailView, LoginRequiredMixin, WriteItInstanceOwnerMixin):
    model = Message
    template_name = "nuntium/profiles/message_detail.html"

    def get_context_data(self, **kwargs):
        context = super(MessageDetail, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.object.writeitinstance
        return context


class MessageDelete(WriteItRelatedModelMixin, DeleteView, LoginRequiredMixin, WriteItInstanceOwnerMixin):
    model = Message
    template_name = "nuntium/profiles/message_delete_confirm.html"

    def get_success_url(self):
        success_url = reverse(
            'messages_per_writeitinstance',
            kwargs={'pk': self.object.writeitinstance.pk},
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
        success_url = reverse('message_detail', kwargs={'pk': self.message.pk})
        return success_url


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


class ModerationView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.message = get_object_or_404(Message, id=kwargs['pk'])
        if self.message.writeitinstance.owner != self.request.user:
            raise Http404
        return super(ModerationView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.message.moderate()

        url = reverse(
            'messages_per_writeitinstance',
            kwargs={'pk': self.message.writeitinstance.pk},
            )
        return redirect(url)


class WriteitPopitRelatingView(WriteItInstanceOwnerMixin, FormView):
    form_class = RelatePopitInstanceWithWriteItInstance
    template_name = 'nuntium/profiles/writeitinstance_and_popit_relations.html'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_writeitinstance()
        return super(WriteitPopitRelatingView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(WriteitPopitRelatingView, self).get_form_kwargs()
        kwargs['writeitinstance'] = self.get_writeitinstance()
        return kwargs

    def get_success_url(self):
        writeitinstance = self.get_writeitinstance()
        url = reverse('writeitinstance_basic_update', kwargs={'pk': writeitinstance.pk})
        return url

    def form_valid(self, form):
        form.relate()
        # It returns an AsyncResult http://celery.readthedocs.org/en/latest/reference/celery.result.html
        # that we could use for future information about this process
        view_messages.add_message(self.request, view_messages.INFO, _("We are now getting the people from popit"))
        response = super(WriteitPopitRelatingView, self).form_valid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super(WriteitPopitRelatingView, self).get_context_data(**kwargs)
        context['relations'] = self.object.writeitinstancepopitinstancerecord_set.all()
        return context


class WriteItDeleteView(WriteItInstanceOwnerMixin, DeleteView):
    model = WriteItInstance

    def get_success_url(self):
        url = reverse('your-instances')
        return url
