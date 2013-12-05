from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from nuntium.views import HomeTemplateView, MessageSearchView, UserAccountView, WriteItInstanceDetailView, WriteItInstanceUpdateView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeTemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^search/?$', MessageSearchView(), name='search_messages'),
    url(r'^accounts/profile/?$', UserAccountView.as_view(), name='account'),


    url(r'^writeitinstance/edit/(?P<pk>[-\d]+)/?$', WriteItInstanceUpdateView.as_view(), name = 'writeitinstance_update'),


    # url(r'^writeit/', include('writeit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^', include('nuntium.subdomain_urls')),

)
