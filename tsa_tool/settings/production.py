from .base import *
import sys
from pathlib import Path


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Must mention ALLOWED_HOSTS in production!
#ALLOWED_HOSTS = ['0.0.0.0']
ALLOWED_HOSTS = ['narwhal.cgm.ntu.edu.tw']

# Turn off debug while imported by Celery with a workaround
# See http://stackoverflow.com/a/4806384
if 'celery' in sys.argv[0]:
    DEBUG = False

# Show emails to console in DEBUG mode
# email setting
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = 'NARWHAL <no_reply@sakura.idv.tw>'
EMAIL_SENDER_ADDRESS = env.str('EMAIL_SENDER_ADDRESS')


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

