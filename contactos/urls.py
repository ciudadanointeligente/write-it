from django.conf.urls import patterns, url
from contactos.views import ContactoUpdateView, ContactCreateView, ToggleContactEnabledView

urlpatterns = patterns('',
    url(r'^contacto/update/(?P<pk>[-\d]+)/?$',
        ContactoUpdateView.as_view(),
        name='contact_value_update'),
    url(r'^(?P<pk>[-\d]+)/(?P<person_pk>[-\d]+)/contacto/create/?$',
        ContactCreateView.as_view(),
        name='create-new-contact'),
    url(r'^contacto/toggle-enabled/(?P<pk>[-\d]+)/?$',
        ToggleContactEnabledView.as_view(),
        name='toggle-enabled'),

)
