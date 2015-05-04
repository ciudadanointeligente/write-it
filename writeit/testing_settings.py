import os
## TESTING ENVIRONMENT
LOCAL_ELASTICSEARCH = True
SOUTH_TESTS_MIGRATE = False
CELERY_ALWAYS_EAGER = True
TRAVIS = os.environ.get('TRAVIS')


if TRAVIS:
    DB = os.environ.get('DB')

    if DB == 'postgres':
        default_db = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'writeit',
            # The following settings are not used with sqlite3:
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '',
            }
    elif DB == 'mysql':
        default_db = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'writeit',
            # The following settings are not used with sqlite3:
            'USER': 'travis',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            }
    else:
        default_db = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'writeit.db',                      # Or path to database file if using sqlite3.
            }

    DATABASES = {'default': default_db}
