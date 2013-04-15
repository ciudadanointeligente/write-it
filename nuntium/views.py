# Create your views here.
from django.views.generic import TemplateView
from nuntium.models import Instance



class HomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        all_instances = Instance.objects.all()


        context['instances'] = all_instances
        return context
