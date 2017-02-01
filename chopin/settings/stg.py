from base import *  # noqa

CACHE_REDIS_DATABASE = '1'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379:' + CACHE_REDIS_DATABASE
BROKER_URL = 'redis://127.0.0.1:6379:' + CACHE_REDIS_DATABASE

INTERNAL_IPS = ('ocve3-stg.dighum.kcl.ac.uk',)
ALLOWED_HOSTS = ['ocve3-stg.dighum.kcl.ac.uk', 'www.chopinonline.ac.uk']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'app_ocve_merged_stg',
        'USER': 'app_ocve',
        'PASSWORD': '',
        'HOST': 'db-pg-1.cch.kcl.ac.uk'
    }
}

HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = PROJECT_NAME + '_stg'

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from local import *  # noqa
except ImportError:
    pass
