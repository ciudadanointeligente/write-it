from django.conf.urls import patterns, url
from contactos.views import ContactoUpdateView, ContactCreateView

urlpatterns = patterns('',
    url(r'^contacto/update/(?P<pk>[-\d]+)/?$',
        ContactoUpdateView.as_view(),
        name='contact_value_update'),
    url(r'^(?P<pk>[-\d]+)/contacto/create/?$',
        ContactCreateView.as_view(),
        name='create-new-contact'),
)
