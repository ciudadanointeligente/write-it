from django.views.generic.edit import UpdateView
from .models import MailItTemplate
from .forms import MailitTemplateForm
from django.core.urlresolvers  import reverse
from django.shortcuts import get_object_or_404
from django.http import Http404
from nuntium.models import WriteItInstance
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class MailitTemplateUpdateView(UpdateView):
    model = MailItTemplate
    form_class = MailitTemplateForm

    @method_decorator(login_required)
    def dispatch(self,*args, **kwargs):
        return super(MailitTemplateUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        self.writeitinstance = get_object_or_404(WriteItInstance, pk=self.kwargs['pk'])
        if not self.writeitinstance.owner.__eq__(self.request.user):
            raise Http404
        self.object = self.writeitinstance.mailit_template
        return self.object

    def get_form_kwargs(self):
        kwargs = super(MailitTemplateUpdateView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs['writeitinstance'] = self.object.writeitinstance
        return kwargs

    def get_success_url(self):
        return reverse('writeitinstance_template_update', kwargs={'pk':self.writeitinstance.pk})
