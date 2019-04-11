# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bo+xba@bth5!wfue6p&f2-$l9kuv9nv1(pdq8+!u3ars61l!qr'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'recipe_app',
        'USER': 'postgres',
        'PASSWORD': 'P@ss1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
