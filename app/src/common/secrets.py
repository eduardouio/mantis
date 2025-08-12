from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.dev-7.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'notificaciones@dev-7.com'
MAIL_PASS = 'bPBc[SK.u-zB'


DATABASES = {
    'TEST': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': 'prod_peisol',
        'USER': 'postgres',
        'PASSWORD': '12Cs5003!!',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'PRODUCTION': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': 'test_peisol',
        'USER': 'postgres',
        'PASSWORD': '12Cs5003!!',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'DEVELOPMENT': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': 'development_peisol',
        'USER': 'eduardo',
        'PASSWORD': 'elian.2011',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


DEFAULT_DB = {
    'default': DATABASES['DEVELOPMENT']
}

# Crear bases de datos
# CREATE DATABASE prod_kosmo OWNER postgres;
# GRANT ALL PRIVILEGES ON DATABASE prod_kosmo TO postgres;

# CREATE DATABASE test_kosmo OWNER postgres;
# GRANT ALL PRIVILEGES ON DATABASE test_kosmo TO postgres;
