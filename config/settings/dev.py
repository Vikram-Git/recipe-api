from config.settings.base import *

SECRET_KEY = 'bo+xba@bth5!wfue6p&f2-$l9kuv9nv1(pdq8+!u3ars61l!qr'

DEBUG = True

ALLOWED_HOSTS = []

# Travis Setup
if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'travisdb',
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }
# Development setup    
else:
    try:
        from config.settings.local import DATABASES
    except:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }



