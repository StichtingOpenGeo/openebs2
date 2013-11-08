DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', 
        'NAME': 'openebs',
        'USER': 'openebs',
        'PASSWORD': 'openebs',
        'HOST': 'localhost',       
        'PORT': '5432',    
    }
}

def custom_show_toolbar(request):
    return True  # Always show toolbar, for example purposes only.

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'ENABLE_STACKTRACES' : True,
    'HIDDEN_STACKTRACE_MODULES': ('gunicorn', 'newrelic'),
}