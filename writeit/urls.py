from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

from tastypie.api import Api

from nuntium.views import RootRedirectView
from nuntium.api import WriteItInstanceResource, MessageResource, AnswerCreationResource, HandleBouncesResource, PersonResource
from nuntium.urls import managepatterns


# Uncomment the next two lines to enable the admin:
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(WriteItInstanceResource())
v1_api.register(MessageResource())
v1_api.register(AnswerCreationResource())
v1_api.register(HandleBouncesResource())
v1_api.register(PersonResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', RootRedirectView.as_view()),

    (r'^api/', include(v1_api.urls)),
    url(r'^social_auth/', include('social.apps.django_app.urls', namespace='social')),

    # TODO: These can probably be removed at some point.
    url(r'^contactos/', include('contactos.urls')),
)

urlpatterns += i18n_patterns('',

    url(r'^(?P<slug>[-\w]+)/manage/', include(managepatterns)),
    url(r'^', include('nuntium.urls')),

    url(r'^', include('nuntium.user_section.urls')),
    url(r'^writeit_instances/', include('nuntium.subdomain_urls')),

    (r'accounts/', include('django.contrib.auth.urls')),
)
