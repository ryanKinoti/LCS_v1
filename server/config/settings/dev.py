from .base import *

DEBUG = os.getenv('DEBUG', 'False')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')

# Logging Settings
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
APP_LOGS = os.path.join(LOGS_DIR, 'app')
DJANGO_LOGS = os.path.join(LOGS_DIR, 'django')
ERROR_LOGS = os.path.join(LOGS_DIR, 'errors')

for directory in [APP_LOGS, DJANGO_LOGS, ERROR_LOGS]:
    os.makedirs(directory, exist_ok=True)

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
