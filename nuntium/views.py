from datetime import date, datetime

from django.db.models import Prefetch
from django.views.generic import TemplateView, DetailView, RedirectView, ListView
from subdomains.utils import reverse
from django.http import Http404, HttpResponseRedirect
from formtools.wizard.views import NamedUrlSessionWizardView
from django.shortcuts import get_object_or_404, redirect

from haystack.views import SearchView
from itertools import chain
from django.db.models import Q
from instance.models import PopoloPerson, WriteItInstance
from popolo.models import Membership
from .models import Confirmation, Message, Moderation
from .forms import MessageSearchForm, PerInstanceSearchForm

from nuntium import forms


class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = WriteItInstance.objects.order_by('slug')

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
        recent_messages = Message.public_objects.filter(writeitinstance=self.object).order_by('-created')[:5]
        context['recent_messages'] = recent_messages
        return context

FORMS = [("who", forms.WhoForm),
         ("draft", forms.DraftForm),
         ("preview", forms.PreviewForm)]

TEMPLATES = {"who": "write/who.html",
             "draft": "write/draft.html",
             "preview": "write/preview.html"}


def _get_persons_prefetch(writeitinstance):
    prefetch_args = ['contact_set']
    if writeitinstance.config.include_area_names:
        prefetch_args.append(
            Prefetch(
                'memberships',
                queryset=Membership.objects.filter(
                    organization__classification='legislature'
                ).select_related('area')))
    return prefetch_args


def _get_person_select_kwargs(writeitinstance):
    prefetch_args = _get_persons_prefetch(writeitinstance)
    # FIXME: far from ideal. We only want to include current
    # politicians in the select. Some instances have memberships with
    # a particular legislative_period_id indicating which term the
    # person is a member of (although unfortunately django-popolo
    # doesn't include that attribute). Other instances don't have any
    # memberships at all, in which case we include all people. We can
    # get this roughly right by filtering for people with *any*
    # current membership if the instance has any memberships at all.
    person_conditions = []
    if writeitinstance.has_popolo_memberships:
        today = date.today()
        person_conditions += [
            Q(memberships__end_date__gte=today) |
            Q(memberships__end_date='') |
            Q(memberships__end_date__isnull=True),
            Q(memberships__start_date__lte=today) |
            Q(memberships__start_date='') |
            Q(memberships__start_date__isnull=True)]
    return {
        'persons_queryset':
        writeitinstance.persons \
            .filter(*person_conditions) \
            .prefetch_related(*prefetch_args) \
            .order_by('name'),
        'include_area_names':
        writeitinstance.config.include_area_names
    }


def _get_person_select_args(writeitinstance):
    as_kwargs = _get_person_select_kwargs(writeitinstance)
    return [
        as_kwargs[k] for k in
        ('persons_queryset', 'include_area_names')
    ]


class WriteMessageView(NamedUrlSessionWizardView):
    form_list = FORMS

    def dispatch(self, request, *args, **kwargs):
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=request.subdomain)
        return super(WriteMessageView, self).dispatch(request=request, *args, **kwargs)

    def get(self, *args, **kwargs):
        the_person = None

        # If we have an ID in the URL and it matches someone, go straight to
        # /draft
        if kwargs.get('step') == 'who' and 'person_id' in self.request.GET:
            person_id = self.request.GET['person_id']
            try:
                the_person = self.writeitinstance.persons.get(
                    identifiers__scheme='popit_id',
                    identifiers__identifier=person_id)
            except PopoloPerson.DoesNotExist:
                pass

        # If we've come to /who but there is only one person possible to
        # contact, go straight to /draft
        if self.steps.current == 'who' and self.writeitinstance.persons_with_contacts.count() == 1:
            the_person = self.writeitinstance.persons_with_contacts.first()

        if the_person is not None:
            self.storage.set_step_data('who', {self.get_form_prefix() + '-persons': [the_person.id]})
            self.storage.current_step = 'draft'
            return redirect(self.get_step_url('draft'))

        # Check that the form contains valid data
        if self.steps.current == 'preview' or self.steps.current == 'draft':
            message = self.get_form_values()
            if not message.get('persons'):
                # Form is missing persons, restart process
                self.storage.reset()
                self.storage.current_step = self.steps.first
                return redirect(self.get_step_url(self.steps.first))
        return super(WriteMessageView, self).get(*args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_kwargs(self, step):
        if step == 'who':
            return _get_person_select_kwargs(self.writeitinstance)
        elif step == 'draft':
            return {'allow_anonymous_messages': self.writeitinstance.config.allow_anonymous_messages}
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
            if form_obj.is_bound:
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
        # Doing anything with the moderations?
        Moderation.objects.filter(message=message)

        return HttpResponseRedirect(reverse('write_message_sign', subdomain=self.writeitinstance.slug))

    def get_context_data(self, form, **kwargs):
        context = super(WriteMessageView, self).get_context_data(form=form, **kwargs)
        context['writeitinstance'] = self.writeitinstance
        if self.steps.current == 'who':
            context['persons'] = self.writeitinstance.persons.all()
        if self.steps.current == 'preview' or self.steps.current == 'draft':
            context['message'] = self.get_form_values()
            context['message']['people'] = context['message'].get('persons')
        return context

    def get_form_prefix(self, *args, **kwargs):
        prefix = super(WriteMessageView, self).get_form_prefix(*args, **kwargs)
        prefix += u"_" + self.writeitinstance.slug
        return prefix


class ConfirmView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        confirmation = get_object_or_404(Confirmation, key=kwargs['slug'])
        # Now proceed with the confirmation
        if confirmation.confirmated_at is None:
            confirmation.confirmated_at = datetime.now()
            confirmation.save()
            confirmation.message.recently_confirmated()
            self.request.session['user_came_via_confirmation_link'] = True
        return reverse('thread_read',
            subdomain=confirmation.message.writeitinstance.slug,
            kwargs={'slug': confirmation.message.slug})


class RootRedirectView(RedirectView):

    permanent = False

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
        if 'pk' in self.kwargs:
            params = {'pk': self.kwargs['pk']}
        elif 'person_id' in self.kwargs:
            params = {
                'identifiers__scheme': 'popit_id',
                'identifiers__identifier': self.kwargs['person_id']}
        self.person = get_object_or_404(PopoloPerson, **params)
        self.writeitinstance = get_object_or_404(WriteItInstance, slug=request.subdomain)
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
        if self.message.author_name == '':
            raise Http404
        return super(MessagesFromPersonView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Message.public_objects.filter(
            writeitinstance=self.writeitinstance,
            author_email=self.message.author_email
        )
        # There's a config option for stricter anonymity, which means
        # that both author_name and author_email must match:
        if self.writeitinstance.config.email_and_name_must_match:
            qs = qs.filter(author_name=self.message.author_name)
        else:
            # By default, don't mix up anonymous (author_name is blank)
            # messages with non-anonymous (author_name is present) messages.
            if self.message.author_name == '':
                qs = qs.filter(author_name='')
            else:
                qs = qs.exclude(author_name='')
        return qs

    def get_context_data(self, **kwargs):
        context = super(MessagesFromPersonView, self).get_context_data(**kwargs)
        context['author_name'] = self.message.author_name
        context['writeitinstance'] = self.writeitinstance
        return context


class MessageThreadsView(ListView):
    model = Message
    template_name = 'thread/all.html'

    def get_queryset(self):
        return Message.public_objects.filter(
            writeitinstance__slug=self.request.subdomain,
        )

    def get_context_data(self, **kwargs):
        context = super(MessageThreadsView, self).get_context_data(**kwargs)
        context['writeitinstance'] = get_object_or_404(WriteItInstance, slug=self.request.subdomain)
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


class MessageThreadView(MessageDetailView):
    model = Message
    template_name = 'thread/read.html'

    def get_context_data(self, **kwargs):
        context = super(MessageThreadView, self).get_context_data(**kwargs)
        if self.request.session.get('user_came_via_confirmation_link', False):
            context['user_came_via_confirmation_link'] = True
            del self.request.session['user_came_via_confirmation_link']

        context['writeitinstance'] = self.object.writeitinstance
        context['awaiting_moderation'] = False
        if self.object.writeitinstance.config.moderation_needed_in_all_messages and \
                self.object.moderated != True and self.object.moderated is not None:
            context['awaiting_moderation'] = True
        return context


class WriteSignView(TemplateView):
    template_name = 'write/sign.html'

    def get_context_data(self, **kwargs):
        context = super(WriteSignView, self).get_context_data(**kwargs)
        context['writeitinstance'] = WriteItInstance.objects.get(slug=self.request.subdomain)
        return context


class MissingContactsView(TemplateView):
    template_name = 'write/missing_contacts.html'

    def get_context_data(self, **kwargs):
        context = super(MissingContactsView, self).get_context_data(**kwargs)
        wii = get_object_or_404(WriteItInstance, slug=self.request.subdomain)
        context['writeitinstance'] = wii
        # We exclude any person with an email address which is not
        # bouncing. (It'd be good to find new email addresses to
        # replace those that are bouncing.)
        context['missing_people'] = wii.persons.exclude(
            contact__is_bounced=False).order_by('name')
        return context


class AboutView(WriteItInstanceDetailView):
    template_name = 'about.html'


class HelpView(TemplateView):
    def get_template_names(self):
        if 'section_name' in self.kwargs:
            return ["help/{}.html".format(self.kwargs['section_name'])]
        else:
            return ["help/index.html"]
