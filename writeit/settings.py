# -*- coding: utf-8 -*-
# Django settings for writeit project.
import sys
import os
DEBUG = True
TASTYPIE_FULL_DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'writeit.db',                    # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

gettext = lambda s: s

LANGUAGES = (
    ('en', gettext('English')),
    ('es', gettext(u'Español')),
    ('ar', gettext(u'العربية')),
    ('fr', gettext(u'Français'))
    )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_YUI_BINARY = '/usr/bin/env yui-compressor'
PIPELINE_COMPILERS = (
    'pipeline.compilers.sass.SASSCompiler',
    )
PIPELINE_SASS_BINARY = '/usr/bin/env sassc'  # Libsass, via libsass-python
PIPELINE_CSS = {
    'writeit-instance': {
        'source_filenames': (
            'sass/instance.scss',
        ),
        'output_filename': 'css/instance.css',
    },
    'writeit-admin': {
        'source_filenames': (
            'sass/admin.scss',
        ),
        'output_filename': 'css/admin.css',
    },
    'writeit-manager': {
        'source_filenames': (
            'sass/manager.scss',
        ),
        'output_filename': 'css/manager.css',
    },
    'writeit-writeinpublic': {
        'source_filenames': (
            'sass/writeinpublic.scss',
        ),
        'output_filename': 'css/writeinpublic.css',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^1rqg8ctiq=#11c*=1mz5pyyry%)t%z^%nrhmh=q%g@r@bej1_'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'writeit.context_processors.web_api_settings',
    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'pagination.middleware.PaginationMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'subdomains.middleware.SubdomainURLRoutingMiddleware',
)

ROOT_URLCONF = 'nuntium.subdomain_urls'

# A dictionary of urlconf module paths, keyed by their subdomain.
SUBDOMAIN_URLCONFS = {
    None: 'writeit.urls',  # no subdomain, e.g. ``example.com``
    'www': 'writeit.urls',
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'writeit.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
TESTING = 'test' in sys.argv

STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage' if TESTING else 'pipeline.storage.PipelineCachedStorage'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'annoying',
    'celery_haystack',

    'djangoplugins',
    'pagination',
    'popit',
    'nuntium',
    'south',
    'contactos',
    'mailit',
    'tastypie',
    'markdown_deux',
    'django_extensions',
    # Searching.
    'haystack',
    'djcelery',
    'pipeline',
    # Uncomment the next line to enable the admin:
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django_object_actions',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # Multi-page form wizard
    'django.contrib.formtools',
    'subdomains',
)

if TESTING:
    INSTALLED_APPS += (
        'django_nose',
        )

#SEARCH INDEX WITH ELASTICSEARCH
HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
if TESTING:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'haystack-testing',
        },
    }
else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'haystack',
        },
    }

#Testing with django
TEST_RUNNER = 'global_test_case.WriteItTestRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'main': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

# POPIT TESTING RELATED
TEST_POPIT_API_HOST_IP = '127.0.0.1'
TEST_POPIT_API_PORT = '3000'
TEST_POPIT_API_SUBDOMAIN = 'popit-django-test'

# We have our local popit instance for testing porpouses running using
# the bash file start_local_popit_api.bash
# create the url to use for testing the database.
# See http://xip.io/ for details on the domain used.
TEST_POPIT_API_URL = "http://%s.%s.xip.io:%s/api" % (
    TEST_POPIT_API_SUBDOMAIN,
    TEST_POPIT_API_HOST_IP,
    TEST_POPIT_API_PORT,
    )


# Email settings
DEFAULT_FROM_EMAIL = 'mailer@example.com'

# DEFAULT_FROM_DOMAIN
DEFAULT_FROM_DOMAIN = 'mailit.ciudadanointeligente.org'

# In some cases it is needed that all emails come from one single
# email address, such is the case when you have just verified a single sender
SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL = False


# CELERY CONFIGURATION
import djcelery
from celery.schedules import crontab
djcelery.setup_loader()

CELERYBEAT_SCHEDULE = {
    # Sends emails every 2 minutes
    'send-mails-every-2-minutes': {
        'task': 'nuntium.tasks.send_mails_task',
        'schedule': crontab(minute='*/2'),
    },
    # Resyncs popit every week
    'resync-popit-apis-every-week': {
        'task': 'nuntium.tasks.pull_from_popit',
        'kwargs': {
            'periodicity': '1W'
        },
        'schedule': crontab(hour=5, minute=30, day_of_week=1),
    },
    # Resyncs popit every day
    'resync-popit-apis-every-day': {
        'task': 'nuntium.tasks.pull_from_popit',
        'kwargs': {
            'periodicity': '1D'
        },
        'schedule': crontab(hour=5, minute=30),
    },
    # Resyncs popit twice every day
    'resync-popit-apis-twice-every-day': {
        'task': 'nuntium.tasks.pull_from_popit',
        'kwargs': {
            'periodicity': '2D'
        },
        'schedule': crontab(hour='*/12'),
    },
}
# the biggest number of recipients a user can
# configure without asking the admin of the site
OVERALL_MAX_RECIPIENTS = 10
# Logs every incoming email??
INCOMING_EMAIL_LOGGING = 'None'

# setting to avoid db changes during test

EXTRA_APPS = ()


# SOCIAL AUTH DETAILS
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'Key'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'S3Cr3t'

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    )

SESSION_COOKIE_DOMAIN = '.127.0.0.1.xip.io'

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_CREATE_MISSING_QUEUES = True

# These can be set independently, but most often one will be set to True and
# the other to False. Setting both to the same boolean value will have
# undefined behaviour.
WEB_BASED = True
API_BASED = False

if TESTING:
    from testing_settings import *  # noqa

try:
    from local_settings import *  # noqa
    INSTALLED_APPS += EXTRA_APPS
except ImportError:
    pass


### HEROKU CONFIGURATION

if 'DATABASE_URL' in os.environ:
    # I thought that in this way I could define that we were in an heroku environment
    import dj_database_url
    DATABASES['default'] = dj_database_url.config()

    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Allow all host headers
    ALLOWED_HOSTS = ['*']

    # Static asset configuration
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = 'staticfiles'
    STATIC_URL = '/static/'

    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )
if 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY' in os.environ:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']

if 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET' in os.environ:
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']

#Email settings
if 'DEFAULT_FROM_EMAIL' in os.environ:
    DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
if 'DEFAULT_FROM_DOMAIN' in os.environ:
    DEFAULT_FROM_DOMAIN = os.environ['DEFAULT_FROM_DOMAIN']
if 'EMAIL_HOST' in os.environ:
    EMAIL_HOST = os.environ['EMAIL_HOST']
if 'EMAIL_PORT' in os.environ:
    EMAIL_PORT = os.environ['EMAIL_PORT']
if 'EMAIL_HOST_USER' in os.environ:
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
if 'EMAIL_HOST_PASSWORD' in os.environ:
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
if 'EMAIL_USE_TLS' in os.environ and os.environ['EMAIL_USE_TLS'] == 'True':
    EMAIL_USE_TLS = True
if 'EMAIL_USE_SSL' in os.environ and os.environ['EMAIL_USE_SSL'] == 'True':
    EMAIL_USE_SSL = True

if 'SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL' in os.environ \
        and os.environ['SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL'] == 'True':
    SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL = True
    # Haystack things elasticsearch
    # HAYSTACK_CONNECTIONS = {
    #     'default': {
    #         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
    #         'URL': os.environ['BONSAI_URL'],
    #         'INDEX_NAME': 'haystack',
    #     },
    # }
