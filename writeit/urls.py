from django.conf.urls import patterns, include, url
from nuntium.views import ConfirmView
from django.conf.urls.i18n import i18n_patterns
from tastypie.api import Api
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'writeit.views.home', name='home'),
    # url(r'^writeit/', include('writeit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^confirm_message/(?P<slug>[-\w]+)/?$', ConfirmView.as_view(), name = 'confirm'),
    (r'^api/', include(v1_api.urls)),
)


urlpatterns += i18n_patterns('',
    
    url(r'^', include('nuntium.urls')),
)
