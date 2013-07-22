from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from nuntium.views import HomeTemplateView, WriteItInstanceDetailView, MessageDetailView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', WriteItInstanceDetailView.as_view(), name = 'instance_detail'),
    url(r'^messages/(?P<slug>[-\w]+)/?$', MessageDetailView.as_view(), name = 'message_detail'),
)
