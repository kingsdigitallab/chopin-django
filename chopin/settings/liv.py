from .base import *  # noqa

CACHE_REDIS_DATABASE = '0'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379:' + CACHE_REDIS_DATABASE
BROKER_URL = 'redis://127.0.0.1:6379:' + CACHE_REDIS_DATABASE

INTERNAL_IPS = ('ocve3.dighum.kcl.ac.uk', )
ALLOWED_HOSTS = ['ocve3.dighum.kcl.ac.uk', 'www.chopinonline.ac.uk',
                 'chopinonline.ac.uk']

# Build JSON with the live flagged sources only
BUILD_LIVE_ONLY = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'app_ocve_merged_test',
        'USER': 'app_ocve',
        'PASSWORD': '',
        'HOST': 'db-pg-1.cch.kcl.ac.uk'
    }
}

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from .local import *  # noqa
except ImportError:
    pass
