#!/bin/bash
# settings.py requires local_settings to exist - point it at the CI database.
set -euo pipefail

cat > openebs2/local_settings.py <<'EOF'
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

SOCIAL_LOGIN_ENABLED = False  # No SSO provider in CI

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'openebs2',
        'USER': 'openebs',
        'PASSWORD': 'openebs',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
EOF
