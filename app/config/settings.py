from pathlib import Path

import os
import sys

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = bool(int(os.environ.get('DEBUG')))
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]
LOCAL_APPS = [
    'apps.lk.apps.LkConfig',
    'apps.bar.apps.BarConfig',
    'apps.iiko.apps.IikoConfig',
    'apps.repairer.apps.RepairerConfig',
    'apps.api.apps.ApiConfig'
]
THIRD_PARTY_APPS = [
    'rest_framework'
]

INSTALLED_APPS = THIRD_PARTY_APPS + DJANGO_APPS + LOCAL_APPS

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.append("django_cprofile_middleware.middleware.ProfilerMiddleware")
else:
    MIDDLEWARE.append("core.middleware.Process500")

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_DEV = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

DATABASE_PROD = {
    'ENGINE': 'django.db.backends.mysql',
    'HOST': os.environ.get('DB_HOST'),
    'NAME': os.environ.get('DB_NAME'),
    'USER': os.environ.get('DB_USER'),
    'PASSWORD': os.environ.get('DB_PASSWORD'),
    'PORT': os.environ.get('DB_PORT'),
}

DATABASES = {
    'default': DATABASE_DEV if DEBUG else DATABASE_PROD
}

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False

USE_TZ = True

LOGOUT_REDIRECT_URL = '/login'

LOGIN_REDIRECT_URL = '/lk'

STATIC_URL = '/assets/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets')]
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

IIKO_API_URL = os.environ.get('IIKO_API_URL')
IIKO_API_LOGIN = os.environ.get('IIKO_API_LOGIN')
IIKO_API_PASSWORD = os.environ.get('IIKO_API_PASSWORD')

TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY')
TELEGRAM_CHAT_ID_FOR_ERRORS = os.environ.get('TELEGRAM_CHAT_ID_FOR_ERRORS')

EXPENSE_SOURCE_CATEGORY = 'Типы оплат'
EXPENSE_TYPE_CATEGORY = 'Расходы.БАР'
FINE_REASON_CATEGORY = 'Штраф'
PAYIN_CATEGORY = 'Внесения'
PAYOUT_CATEGORY = 'Изъятие'
TOVAR_ARRIVAL_CATEGORY = 'Пиво/напитки'

TOVAR_BEER_CATEGORY = 'Пиво разливное'
TOVAR_PRODUCTS_CATEGORY = 'Продукты'
TOVAR_DRINKS_CATEGORY = 'Бар'
TOVAR_HOZ_CATEGORY = 'Хоз. товары'
TOVAR_BOX_CATEGORY = 'Упаковка'
TOVAR_WARE_CATEGORY = 'Посуда'

PAYMENT_TYPE_NAL = 'Наличные'
PAYMENT_TYPE_BN = 'Бизнес-карта'

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_BROKER_TRANSPORT_OPTION = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
