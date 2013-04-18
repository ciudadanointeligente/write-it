# Create your views here.
from django.views.generic import TemplateView, CreateView, DetailView
from django.core.urlresolvers import reverse
from nuntium.models import WriteItInstance
from nuntium.forms import MessageCreateForm



class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = WriteItInstance.objects.all()

        context['writeitinstances'] = all_instances
        return context

class WriteItInstanceDetailView(CreateView):
    form_class = MessageCreateForm
    model = WriteItInstance
    template_name='nuntium/instance_detail.html'

    def get_success_url(self):
        return reverse('instance_detail', kwargs={
            'slug':self.object.writeitinstance.slug
            })

    def get_form_kwargs(self):
        kwargs = super(WriteItInstanceDetailView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs['writeitinstance'] = self.object
        
        return kwargs