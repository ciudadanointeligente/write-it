from datetime import datetime

from django.views.generic import TemplateView, CreateView, DetailView, RedirectView, ListView
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView

from haystack.views import SearchView
from itertools import chain
from popit.models import Person
from django.db.models import Q
from .models import WriteItInstance, Confirmation, Message, Moderation
from .forms import MessageCreateForm, MessageSearchForm, PerInstanceSearchForm
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


FORMS = [("who", forms.WhoForm),
         ("draft", forms.DraftForm),
         ("preview", forms.PreviewForm)]

TEMPLATES = {"who": "write/who.html",
             "draft": "write/draft.html",
             "preview": "write/preview.html"}


class WriteMessageView(NamedUrlSessionWizardView):
    form_list = FORMS

    def dispatch(self, request, *args, **kwargs):
        self.writeitinstance = WriteItInstance.objects.get(slug=kwargs['slug'])
        return super(WriteMessageView, self).dispatch(request=request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_step_url(self, step):
        return reverse(self.url_name, kwargs={'slug': self.kwargs['slug'], 'step': step})

    def process_step(self, form):
        form_data = self.get_form_step_data(form)
        self.storage.extra_data.update(form_data)
        return form_data

    def done(self, form_list, **kwargs):
        do_something_with_the_form_data(form_list)
        return HttpResponseRedirect(reverse('write_message_sign', kwargs={'slug': self.kwargs['slug']}))

    def get_context_data(self, form, **kwargs):
        context = super(WriteMessageView, self).get_context_data(form=form, **kwargs)
        context['writeitinstance'] = self.writeitinstance
        if self.steps.current == 'who':
            context['persons'] = self.writeitinstance.persons.all()
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
        self.slug = kwargs.pop('slug')
        return super(PerInstanceSearchView, self).__call__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        self.writeitinstance = WriteItInstance.objects.get(slug=self.slug)
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs['writeitinstance'] = self.writeitinstance

        return super(PerInstanceSearchView, self).build_form(form_kwargs)


class MessagesPerPersonView(ListView):
    model = Message
    template_name = "nuntium/message/per_person.html"

    def dispatch(self, *args, **kwargs):
        self.person = Person.objects.get(id=self.kwargs['pk'])
        self.subdomain = self.kwargs['slug']
        self.writeitinstance = WriteItInstance.objects.get(slug=self.subdomain)
        return super(MessagesPerPersonView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Message.public_objects.filter(
            person=self.person,
            writeitinstance=self.writeitinstance,
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super(MessagesPerPersonView, self).get_context_data(**kwargs)
        context['person'] = self.person
        return context
