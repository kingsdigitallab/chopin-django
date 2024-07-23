from .base import *  # noqa

#CACHE_REDIS_DATABASE = '2'
#CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE

DEBUG = True

# Image Server Settings
# ------------------------------------------------------------------------------
# Example: http://localhost:8182/iiif/3/38%2f81%2f05%2fImage05.jp2/info.json
# folder slashes should be escaped as above
# '/iiif/3/?zoomify=jp2/ocvejp2-proc/38/81/05/Image05.jp2/'
IIP_URL = '/iipsrv/fcgi-bin/iipsrv.fcgi'
IMAGE_SERVER_URL = ''
# Absolute server path to physical repository of jp2 images
# This should be changed to a physical file location if you plan to use the uploader
IMAGEFOLDER = ''



# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=['localhost'])

INTERNAL_IPS = ['0.0.0.0', '127.0.0.1', '::1', '10.0.2.2']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("POSTGRES_DATABASE"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),
        'HOST': env("POSTGRES_HOST")

    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE':
            'haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine',
        'URL': 'http://elasticsearch:9200/',
        'INDEX_NAME': PROJECT_NAME,
    },
}

