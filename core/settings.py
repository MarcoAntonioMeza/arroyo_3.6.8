from pathlib import Path
import os
import pymysql
pymysql.install_as_MySQLdb()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-oh%%=*u3z#9p%h7l!s7-&3ebye+h7l&mmjix5z00b#ke^bc&^l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
IS_DEVELOPMENT = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'arroyo',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'layouts'), os.path.join(BASE_DIR, 'templates')],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
if IS_DEVELOPMENT:
    DATABASES = {
        'erp': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'pescadosymarisco_erp',
            'USER': 'pescadosymarisco_dash',
            'PASSWORD': 'LS:dash*123',
            'HOST': '162.240.78.82',  # Por ejemplo, '123.45.67.89' o 'mysql.ejemplo.com'
            'PORT': '3306',  # Este es el puerto por defecto de MySQL. Cámbialo si tu servidor usa otro.
        },
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'dash_arroyo',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',  # Por ejemplo, '123.45.67.89' o 'mysql.ejemplo.com'
            'PORT': '3306',  # Este es el puerto por defecto de MySQL. Cámbialo si tu servidor usa otro.
        }
    }
else:
    DATABASES = {
        'erp': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'pescadosymarisco_erp',
            'USER': 'pescadosymarisco_dash',
            'PASSWORD': 'LS:dash*123',
            'HOST': 'localhost',  # Por ejemplo, '123.45.67.89' o 'mysql.ejemplo.com'
            'PORT': '3306',  # Este es el puerto por defecto de MySQL. Cámbialo si tu servidor usa otro.
        },
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'pescadosymarisco_control_dash',
            'USER': 'pescadosymarisco_control_dash',
            'PASSWORD': '^zb[R*(TvjwO',
            'HOST': 'localhost',  # Por ejemplo, '123.45.67.89' o 'mysql.ejemplo.com'
            'PORT': '3306',  # Este es el puerto por defecto de MySQL. Cámbialo si tu servidor usa otro.
        }
    }

#}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # O la ruta donde están tus archivos estáticos
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')# donde se almacenarán los archivos estáticos recolectados


#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login'