"""
Django settings for hp project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/

For production settings see
https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
"""
import environ
import getpass
import logging
import os

import django.utils.text
from ddhldap.settings import *  # noqa
from django.conf import global_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PROJECT_NAME = 'chopin'
PROJECT_TITLE = 'Chopin Online'

COMPOSE_DIR = os.path.join(BASE_DIR, "compose")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    #env.read_env(str(COMPOSE_DIR.path(".env")))
    environ.Env.read_env(os.path.join(COMPOSE_DIR, '.env'))

SITE_TITLE = {
    'aco': 'Annotated Catalogue of Chopin\'s First Editions',
    'cfeo': 'Chopin\'s First Editions Online',
    'ocve': 'Online Chopin Variorum Edition'
}

# -----------------------------------------------------------------------------
# Core Settings
# https://docs.djangoproject.com/en/1.6/ref/settings/#id6
# -----------------------------------------------------------------------------

ADMINS = (
    ('Miguel Vieira', 'jose.m.vieira@kcl.ac.uk'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = []

# https://docs.djangoproject.com/en/1.6/ref/settings/#caches
# https://docs.djangoproject.com/en/dev/topics/cache/
# http://redis.io/topics/lru-cache
# http://niwibe.github.io/django-redis/

# CACHE_REDIS_DATABASE = '0'
#
# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.cache.RedisCache',
#         'LOCATION': '127.0.0.1:6379:' + CACHE_REDIS_DATABASE,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
#             'IGNORE_EXCEPTIONS': True
#         }
#     }
# }

# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
}


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'haystack',
    'modelcluster',
    'taggit',
    'tinymce',
    'registration',
    'wagtail.core',
    'wagtail.admin',
    'wagtail.documents',
    'wagtail.snippets',
    'wagtail.search',
    'wagtail.users',
    'wagtail.images',
    'wagtail.embeds',
    'wagtail.contrib.redirects',
)

INSTALLED_APPS += (
    'catalogue',
    'chopin',
    'ocve',
)

INTERNAL_IPS = ('127.0.0.1', )


LOGGING_ROOT = os.path.join(BASE_DIR, 'logs')
LOGGING_LEVEL = logging.INFO

if not os.path.exists(LOGGING_ROOT):
    os.makedirs(LOGGING_ROOT)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s '
                       '%(process)d %(thread)d %(message)s')
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'django.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'django_auth_ldap': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'catalogue': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'catalogue.tasks': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'chopin': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
    }
}


MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware'
]

ROOT_URLCONF = PROJECT_NAME + '.urls'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# )

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                'catalogue.context_processors.settings',
                'ocve.context_processors.ocve_constants',
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": False,
        },
    },
]

# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = False
USE_TZ = True

WSGI_APPLICATION = PROJECT_NAME + '.wsgi.application'


# -----------------------------------------------------------------------------
# Authentication
# https://docs.djangoproject.com/en/1.6/ref/settings/#auth
# https://scm.cch.kcl.ac.uk/hg/ddhldap-django
# -----------------------------------------------------------------------------


AUTH_LDAP_REQUIRE_GROUP = 'cn=ocve,' + LDAP_BASE_OU


# -----------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
# https://docs.djangoproject.com/en/1.6/ref/settings/#static-files
# -----------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip('/'))

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'assets'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL.strip('/'))

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)


# -----------------------------------------------------------------------------
# Installed Applications Settings
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Catalogue
# -----------------------------------------------------------------------------

AC_ENCODING = 'UTF-8'

CFEO_BASE_URL = '/cfeo/browse/acview/'
OCVE_BASE_URL = '/ocve/browse/acview/'

WORKS_WITHOUT_OPUS = ['GDC', 'HEX', 'MEG', 'MFM', 'MazG&Bflat', 'PolGm', 'MM',
                      'VGNA']
POSTHUMOUS_WORKS_WITH_OPUS = 66
POSTHUMOUS_WORKS_WITHOUT_OPUS = ['MazC', 'MazG&Bflat', 'Mazd,Bflat,G,Lento',
                                 'PolGflat', 'PolGsharpm', 'Posth', 'WaltzE',
                                 'WaltzEm']
ALL_WORKS_WITHOUT_OPUS = WORKS_WITHOUT_OPUS + POSTHUMOUS_WORKS_WITHOUT_OPUS

# -----------------------------------------------------------------------------
# Celery
# http://docs.celeryproject.org/en/latest/
# -----------------------------------------------------------------------------

# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/' + CACHE_REDIS_DATABASE
# BROKER_URL = 'redis://127.0.0.1:6379/' + CACHE_REDIS_DATABASE
#
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# CELERYBEAT_SCHEDULE = {
#     'haystack-update-index-every-day': {
#         'task': 'catalogue.tasks.haystack_update_index',
#         'schedule': crontab(minute=0, hour=2),
#     },
# }

# -----------------------------------------------------------------------------
# CMS
# -----------------------------------------------------------------------------

ITEMS_PER_PAGE = 10
ALLOW_COMMENTS = True
DISQUS_SHORTNAME = None

# -----------------------------------------------------------------------------
# Django Compressor
# http://django-compressor.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# -----------------------------------------------------------------------------
# Django Grappelli
# http://django-grappelli.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

GRAPPELLI_ADMIN_TITLE = PROJECT_TITLE

# -----------------------------------------------------------------------------
# Django Haystack
# http://django-haystack.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE':
        "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': PROJECT_NAME,
        'TIMEOUT': 60 * 5,
        'BATCH_SIZE': 10,
    }
}

HAYSTACK_LIMIT_TO_REGISTERED_MODELS = False

# -----------------------------------------------------------------------------
# FABRIC
# -----------------------------------------------------------------------------

FABRIC_USER = getpass.getuser()

# -----------------------------------------------------------------------------
# IIP
# -----------------------------------------------------------------------------

IIP_URL = '/iip/iipsrv.fcgi'
IMAGE_SERVER_URL = 'https://ocve3-images.dighum.kcl.ac.uk/iip/iipsrv.fcgi'
# Absolute server path to physical repository of jp2 images
IMAGEFOLDER = '/vol/ocve3/images/'

# -----------------------------------------------------------------------------
# OCVE
# -----------------------------------------------------------------------------

SOURCEJSONPATH = os.path.join('assets', 'javascripts')

# Build JSON with the live flag
BUILD_LIVE_ONLY = False

IMAGE_UPLOAD_PATH = '/vol/ocve2/images/upload/'
CONVERTED_UPLOAD_PATH = '/vol/ocve2/images/temp/'
NEWJP2_UPLOAD_PATH = '/vol/ocve2/images/jp2/newjp2/'
UPLOAD_EXTENSION = '.tif'

# The width of the image when extracting bar region thumbnails in iip
THUMBNAIL_WIDTH = 500

# Height of images in bar-view template
BAR_IMAGE_HEIGHT = 200

# Folder where thumbnails generated from iip reside
THUMBNAIL_DIR = '/vol/ocve3/images/thumbnails/'

# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------

ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_HOST = 'smtp.cch.kcl.ac.uk'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'noreply@kcl.ac.uk'

# -----------------------------------------------------------------------------
# TinyMCE
# -----------------------------------------------------------------------------

TINYMCE_DEFAULT_CONFIG = {
    'mode': 'textareas',
    'plugins': 'paste,searchreplace,xhtmlxtras',
    'theme': 'advanced',
    'theme_advanced_buttons1': 'bold,italic,sup,sub,undo,redo',
    'theme_advanced_buttons2': '',
    'theme_advanced_buttons3': '',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_statusbar_location': 'bottom',
    'theme_advanced_resizing': True,
}

# -----------------------------------------------------------------------------
# Wagtail
# http://wagtail.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

WAGTAIL_SITE_NAME = PROJECT_TITLE

WAGTAILSEARCH_RESULTS_TEMPLATE = "search_results.html"

WAGTAILSEARCH_INDEX = PROJECT_NAME

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.elasticsearch7",
        "URLS": ["http://127.0.0.1:9200"],
        "INDEX": WAGTAILSEARCH_INDEX,
        "TIMEOUT": 5,
        "FORCE_NEW": False,
    }
}


# Allow all manner of non-alphanumeric characters in filenames, since
# the PDF files for Works/Impressions use them meaningfully.
def get_valid_filename(s):
    from django.utils.encoding import force_text
    return force_text(s).strip().replace(' ', '_')

django.utils.text.get_valid_filename = get_valid_filename

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
