from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from .views import HomeTemplateView, WriteItInstanceDetailView, \
						MessageDetailView, PerInstanceSearchView, \
						MessagesPerPersonView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = i18n_patterns('',
    # Examples:
    url(r'^$', WriteItInstanceDetailView.as_view(), name = 'instance_detail'),
    url(r'^messages/(?P<slug>[-\w]+)/?$', MessageDetailView.as_view(), name = 'message_detail'),
    url(r'^search/?$', PerInstanceSearchView(), name='instance_search'),
    url(r'^per_person/(?P<pk>[-\d]+)/?$', MessagesPerPersonView.as_view(),
    				 name='messages_per_person'),
)
