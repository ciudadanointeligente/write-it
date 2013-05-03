from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, DetailView
from nuntium.views import HomeTemplateView, WriteItInstanceDetailView, ConfirmView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeTemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^instances/(?P<slug>[-\w]+)/?$', WriteItInstanceDetailView.as_view(), name = 'instance_detail'),
    url(r'^confirm_message/(?P<slug>[-\w]+)/?$', ConfirmView.as_view(), name = 'confirm'),
    # url(r'^writeit/', include('writeit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
