from datetime import datetime

from django.views.generic import TemplateView, DetailView, RedirectView, ListView
from subdomains.utils import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.shortcuts import get_object_or_404

from haystack.views import SearchView
from itertools import chain
from popit.models import Person
from django.db.models import Q
from .models import WriteItInstance, Confirmation, Message, Moderation
from .forms import MessageSearchForm, PerInstanceSearchForm

from nuntium import forms


class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = WriteItInstance.objects.all()

        context['writeitinstances'] = all_instances
        return context


class WriteItInstanceListView(ListView):
    model = WriteItInstance

    def get_queryset(self, *args, **kwargs):
        '''
        This filters the instances that are
        in testing_mode = True only if you are logged in
        and you own the instance
        '''
        original_queryset = super(WriteItInstanceListView, self).get_queryset(*args, **kwargs)
        for ins in original_queryset:
            if ins.config is None:
                ins.config
        user = self.request.user
        queryset = original_queryset.filter(Q(config__testing_mode=False))
        if user.id:
            instances_owned_by_user = original_queryset.filter(
                Q(config__testing_mode=True)).filter(Q(owner=user))
        else:
            instances_owned_by_user = queryset.none()
        queryset = list(chain(instances_owned_by_user, queryset))

        '''
        The tests for this code can be found at nuntium/tests/home_view_tests.py
        '''
        return queryset


class WriteItInstanceDetailView(DetailView):
    model = WriteItInstance
    template_name = 'nuntium/instance_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['slug'] = request.subdomain
        return super(WriteItInstanceDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WriteItInstanceDetailView, self).get_context_data(**kwargs)
        recent_messages = Message.public_objects.filter(writeitinstance=self.object).order_by('created')[:5]
        context['recent_messages'] = recent_messages
        return context

FORMS = [("who", forms.WhoForm),
         ("draft", forms.DraftForm),
         ("preview", forms.PreviewForm)]

TEMPLATES = {"who": "write/who.html",
             "draft": "write/draft.html",
             "preview": "write/preview.html"}


class WriteMessageView(NamedUrlSessionWizardView):
    form_list = FORMS

    def dispatch(self, request, *args, **kwargs):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=request.subdomain)
        return super(WriteMessageView, self).dispatch(request=request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_kwargs(self, step):
        if step == 'who':
            # FIXME: Do we actually want .all() here?
            return {'persons_queryset': self.writeitinstance.persons.all()}
        else:
            return {}

    def get_form_values(self):
        """
        This code is taken from the django form wizards views.py
        Returns a dictionary of all form values
        """
        final_form_list = []
        # walk through the form list and try to validate the data again.
        for form_key in ['who', 'draft']:
            form_obj = self.get_form(step=form_key,
                data=self.storage.get_step_data(form_key),
                files=self.storage.get_step_files(form_key))
            form_obj.is_valid()
            final_form_list.append(form_obj)
        data = {}
        [data.update(form.cleaned_data) for form in final_form_list]
        return data

    def done(self, form_list, **kwargs):
        data = {}
        [data.update(form.cleaned_data) for form in form_list]
        # Save a message object here
        message = Message(writeitinstance=self.writeitinstance, **data)
        message.save()
        Confirmation.objects.create(message=message)
        moderations = Moderation.objects.filter(message=message)
        if moderations.count() > 0 or self.writeitinstance.config.moderation_needed_in_all_messages:
            messages.success(self.request, _("Please confirm your email address. We have sent a confirmation link to %(email)s. After that your message will be waiting for moderation.") % {'email': message.author_email})
        else:
            messages.success(self.request, _("Please confirm your email address. We have sent a confirmation link to %(email)s.") % {'email': message.author_email})
        return HttpResponseRedirect(reverse('write_message_sign', subdomain=self.writeitinstance.slug))

    def get_context_data(self, form, **kwargs):
        context = super(WriteMessageView, self).get_context_data(form=form, **kwargs)
        context['writeitinstance'] = self.writeitinstance
        if self.steps.current == 'who':
            context['persons'] = self.writeitinstance.persons.all()
        if self.steps.current == 'preview':
            context['message'] = self.get_form_values()
        return context


class MessageDetailView(DetailView):
    template_name = 'nuntium/message/message_detail.html'
    model = Message

    def get_queryset(self):
        qs = Message.objects.filter(slug__iexact=self.kwargs['slug'])
        return qs

    def get_object(self):
        the_message = super(MessageDetailView, self).get_object()
        if not the_message.public:
            raise Http404
        if not (the_message.confirmated or the_message.confirmation.is_confirmed):
            raise Http404
        return the_message


class ConfirmView(DetailView):
    template_name = 'nuntium/confirm.html'
    model = Confirmation
    slug_field = 'key'

    def dispatch(self, *args, **kwargs):
        confirmation = super(ConfirmView, self).get_object()
        if confirmation.confirmated_at is not None:
            raise Http404
        return super(ConfirmView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        confirmation = super(ConfirmView, self).get_object(queryset)

        return confirmation

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context['writeitinstance'] = self.object.message.writeitinstance
        return context

    def get(self, *args, **kwargs):
        confirmation = self.get_object()
        confirmation.confirmated_at = datetime.now()
        confirmation.save()
        confirmation.message.recently_confirmated()
        return super(ConfirmView, self).get(*args, **kwargs)


class ModerationView(DetailView):
    model = Moderation
    slug_field = 'key'


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
        self.get_object().message.delete()
        return get


class RootRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):

        url = reverse("home")
        return url


class MessageSearchView(SearchView):
    def __init__(self, *args, **kwargs):
        super(MessageSearchView, self).__init__(*args, **kwargs)
        self.form_class = MessageSearchForm
        self.template = 'nuntium/search.html'


class PerInstanceSearchView(SearchView):
    def __init__(self, *args, **kwargs):
        super(PerInstanceSearchView, self).__init__(*args, **kwargs)
        self.form_class = PerInstanceSearchForm
        self.template = 'nuntium/instance_search.html'

    def __call__(self, *args, **kwargs):
        request = args[0]
        self.slug = request.subdomain
        return super(PerInstanceSearchView, self).__call__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        self.writeitinstance = WriteItInstance.objects.get(slug=self.slug)
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs['writeitinstance'] = self.writeitinstance

        return super(PerInstanceSearchView, self).build_form(form_kwargs)


class MessagesPerPersonView(ListView):
    model = Message
    template_name = "thread/to.html"

    def dispatch(self, request, *args, **kwargs):
        self.person = Person.objects.get(pk=self.kwargs['pk'])
        self.writeitinstance = WriteItInstance.objects.get(slug=request.subdomain)
        return super(MessagesPerPersonView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Message.public_objects.filter(
            person=self.person,
            writeitinstance=self.writeitinstance,
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super(MessagesPerPersonView, self).get_context_data(**kwargs)
        context['person'] = self.person
        context['writeitinstance'] = self.writeitinstance
        return context


class MessagesFromPersonView(ListView):
    model = Message
    template_name = 'nuntium/message/from_person.html'

    def dispatch(self, *args, **kwargs):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=self.request.subdomain)
        self.message = get_object_or_404(Message, slug=self.kwargs['message_slug'])
        return super(MessagesFromPersonView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super(MessagesFromPersonView, self).get_queryset()
        qs = qs.filter(writeitinstance=self.writeitinstance).\
            filter(public=True).filter(confirmated=True).\
            filter(author_email=self.message.author_email)
        return qs

    def get_context_data(self, **kwargs):
        context = super(MessagesFromPersonView, self).get_context_data(**kwargs)
        context['author_name'] = self.message.author_name
        return context


class MessageThreadsView(ListView):
    model = Message
    template_name = 'thread/all.html'

    def get_queryset(self):
        queryset = super(MessageThreadsView, self).get_queryset()
        return queryset.filter(writeitinstance__slug=self.request.subdomain)


class MessageThreadView(DetailView):
    model = Message
    template_name = 'thread/read.html'

    def get_object(self):
        the_message = super(MessageThreadView, self).get_object()
        if not the_message.public:
            raise Http404
        if not (the_message.confirmated or the_message.confirmation.is_confirmed):
            raise Http404
        return the_message

    def get_context_data(self, **kwargs):
        context = super(MessageThreadView, self).get_context_data(**kwargs)

        context['writeitinstance'] = self.object.writeitinstance
        return context
