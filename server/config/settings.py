import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

from config.logs_config import ColorFormatter

load_dotenv()

# Base Settings
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

AUTH_LOGS = os.path.join(LOGS_DIR, 'auth')
ERROR_LOGS = os.path.join(LOGS_DIR, 'errors')
INFO_LOGS = os.path.join(LOGS_DIR, 'info')
FIREBASE_LOGS = os.path.join(LOGS_DIR, 'firebase')

for directory in [AUTH_LOGS, ERROR_LOGS, INFO_LOGS, FIREBASE_LOGS]:
    os.makedirs(directory, exist_ok=True)

# Application Settings
INSTALLED_APPS = [
    'django.contrib.admin',
    'apps.accounts.apps.AccountsConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_seed',
    'apps.services.apps.ServicesConfig',
    'apps.inventory.apps.InventoryConfig',
    'apps.finances.apps.FinancesConfig',
    'apps.bookings.apps.BookingsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.firebase.FirebaseAuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

FIREBASE_MIDDLEWARE_EXEMPT_URLS = [
    '/admin/',
    '/admin/login/',
    '/admin/logout/',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': []
        ,
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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Your React dev server
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Session Settings
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_DOMAIN = '127.0.0.1' if DEBUG else None

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000"
]
CSRF_USE_SESSIONS = True
CSRF_COOKIE_DOMAIN = '127.0.0.1' if DEBUG else None

# Firebase Settings
FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, "firebase_credentials.json")
FIREBASE_AUTH_CHECK_REVOKED = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_THROTTLE_CLASSES': [
        'utils.throttling.UserActionThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
        'user': '60/minute',
    }
}
