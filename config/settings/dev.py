from config.settings.base import *


try:
    from config.settings.local import *
except:
    SECRET_KEY = 'bo+xba@bth5!wfue6p&f2-$l9kuv9nv1(pdq8+!u3ars61l!qr'
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

