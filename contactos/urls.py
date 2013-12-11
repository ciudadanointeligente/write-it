from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from contactos.views import ContactoUpdateView, ContactCreateView

urlpatterns = patterns('',
    url(r'^contacto/update/(?P<pk>[-\d]+)/?$', 
        ContactoUpdateView.as_view(), 
        name = 'contact_value_update'),
    url(r'^contacto/create/?$', 
        ContactCreateView.as_view(), 
        name = 'create-new-contact'),
)