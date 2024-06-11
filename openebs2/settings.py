# Django settings for openebs2 project.

DEBUG = False

ADMINS = (
    ('Stefan de Konink', 'stefan@opengeo.nl'),
    ('Joel Haasnoot', 'joelhaasnoot+openebs@gmail.com')
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # GeoDjango
        'NAME': 'openebs2',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

ALLOWED_HOSTS = ['localhost', '.openebs.nl']

SITE_ID = 1

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'nl-nl'

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = ''
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
LOGIN_REDIRECT_URL = 'msg_index'  # This is temporary

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["openebs2/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Crispy = form addon
CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap3"

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
)

ROOT_URLCONF = 'openebs2.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'openebs2.wsgi.application'

INSTALLED_APPS = (
    # Django pieces
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    # allauth pieces
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid_connect',

    # Our apps
    # Order matters for testing: openebs depends on kv1 not viceversa
    'kv1',  # Static data stuff
    'openebs',
    'ferry',
    'utils',  # Load our custom filters
    # 'openebs.apps.OpenebsConfig',

    # Libs
    'floppyforms',
    'crispy_forms',
    'crispy_bootstrap3',
    'leaflet',
    # 'debug_toolbar',

    # Admin & tools
    'django.contrib.admin',
)

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Logging so far
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
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
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "/tmp/openebs.log",
            'maxBytes': 5000000,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'verify_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "/tmp/openebs_verify.log",
            'maxBytes': 5000000,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'spoof_logfile': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/tmp/spoofed_requests.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'openebs': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': True
        },
        'openebs.kv8verify': {
            'handlers': ['verify_logfile'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.security.DisallowedHost': {
            'handlers': ['spoof_logfile'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

# Django Leaflet
LEAFLET_CONFIG = {
    'TILES': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'RESET_VIEW': False
}

CALENDAR_LOCALE = 'nl_NL.UTF-8'

# APPLICATION SPECIFIC SETTINGS

# Operator day
CROSSOVER_HOUR = 4

# Verification feed settings
GOVI_VERIFY_FEED = 'tcp://192.168.33.1:8001'  # 'tcp://node02.kv7.openov.nl:7817'
GOVI_VERIFY_SUB = "/InTraffic/KV8gen"

EXTERNAL_MESSAGE_USER_ID = None  # Set in local_settings

FERRY_FULL_REASONTYPE = 3
FERRY_FULL_SUBREASONTYPE = 7
FERRY_FULL_REASONCONTENT = "Boot is vol"

# Push settings
try:
    from openebs2.settings_push import *
except ImportError:
    PUSH_SETTINGS = False

try:
    from openebs2.local_settings import *
except ImportError:
    raise
    pass
