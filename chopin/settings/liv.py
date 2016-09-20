from base import *  # noqa

CACHE_REDIS_DATABASE = '0'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE

INTERNAL_IPS = ('ocve3.dighum.kcl.ac.uk', )
ALLOWED_HOSTS = ['ocve3.dighum.kcl.ac.uk', 'www.chopinonline.ac.uk',
                 'chopinonline.ac.uk']

#Build Json with the live flagged sources only
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

CELERYBEAT_SCHEDULE = {
    'haystack-update-index-every-day': {
        'task': 'catalogue.tasks.haystack_update_index',
        'schedule': crontab(minute=0, hour=2),
    },
    'push-to-liv-daily':{
        'task':'ocve.tasks.push_to_liv',
        'schedule': crontab(minute=0, hour=1),
    }
}

# -----------------------------------------------------------------------------
# Local settings
# -----------------------------------------------------------------------------

try:
    from local import *  # noqa
except ImportError:
    pass
