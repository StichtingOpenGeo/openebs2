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

TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
)
