# Django settings for openebs2 project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Stefan de Konink', 'stefan@opengeo.nl'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # GeoDjango
        'NAME': 'openebs2',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Debug bar config
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

SITE_ID = 1

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'nl-nl'

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

STATIC_ROOT = 'static/'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    "openebs2/static",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'rsy&8z9#0sr4_fpf!p1omymr(!*5upr%p4k7y#d9cz@^et+u)='

LOGIN_URL = 'app_login'
LOGOUT_URL = 'app_logout'
LOGIN_REDIRECT_URL = 'msg_index' # This is temporary

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'openebs2.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'openebs2.wsgi.application'

TEMPLATE_DIRS = (
    "openebs2/templates",
)

INSTALLED_APPS = (
    # Django pieces
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    # Our app
    'openebs',
    'kv1', # Import stuff

    # Libs
    'south',
    'json_field',
    'floppyforms',
    'crispy_forms',
    'leaflet',

    # Admin & tools
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'debug_toolbar'
)

# Logging so far
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': "/tmp/openebs",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
    }
}

# Debug bar config
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

# Crispy = form addon
CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

# ssh joel@openebs.nl -L 8000:91.240.240.195:80 -g #
GOVI_HOST = '192.168.33.1:8000' #'drisacc.transmodel.nl'
GOVI_PATH = '/TMI_Post/KV15'
GOVI_SUBSCRIBER = 'openOV'
GOVI_NAMESPACE = 'http://bison.connekt.nl/tmi8/kv15/msg'
GOVI_DOSSIER = 'KV15messages'

GOVI_PUSH_DEBUG = DEBUG
GOVI_PUSH_SEND = True

try:
    from local_settings import *
except ImportError:
    pass
