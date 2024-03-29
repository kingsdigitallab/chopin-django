from .base import *  # noqa

DEBUG = True

# CACHE_REDIS_DATABASE = '2'
# CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379:' + CACHE_REDIS_DATABASE
# BROKER_URL = 'redis://127.0.0.1:6379:' + CACHE_REDIS_DATABASE

INTERNAL_IPS = ('ocve3-dev.dighum.kcl.ac.uk', )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'app_ocve_merged_test',
        'USER': 'app_ocve',
        'PASSWORD': 'rabbit390Hole',
        'HOST': 'db-pg-1.cch.kcl.ac.uk'
    }
}

LOGGING_LEVEL = logging.DEBUG

LOGGING['loggers']['django_auth_ldap']['level'] = LOGGING_LEVEL
LOGGING['loggers']['catalogue']['level'] = LOGGING_LEVEL
LOGGING['loggers']['catalogue.tasks']['level'] = LOGGING_LEVEL
LOGGING['loggers']['chopin']['level'] = LOGGING_LEVEL

HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = PROJECT_NAME + '_dev'

TEMPLATE_DEBUG = True

# -----------------------------------------------------------------------------
# Django Extensions
# http://django-extensions.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import django_extensions  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)
except ImportError:
    pass

# -----------------------------------------------------------------------------
# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

# try:
#     import debug_toolbar  # noqa
#
#     INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
#     MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
#         'debug_toolbar.middleware.DebugToolbarMiddleware',)
#     DEBUG_TOOLBAR_PATCH_SETTINGS = True
# except ImportError:
#     pass

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from .local import *  # noqa
except ImportError:
    print('failed to import local settings')
    raise ImportError('Error importing local settings')
