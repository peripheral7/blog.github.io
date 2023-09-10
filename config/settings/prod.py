import environ
from .base import *

ALLOWED_HOSTS = ['15.164.140.211', "*"]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = []
DEBUG = False

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': '5432',
    }
}

