from django.conf.urls import patterns, url
from .views import MailitTemplateUpdateView

urlpatterns = patterns(
    '',
    url(r'^edit/(?P<pk>[-\d]+)/?$',
        MailitTemplateUpdateView.as_view(),
        name='mailit-template-update'),
    )
