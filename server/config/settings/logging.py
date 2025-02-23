from .log_config import ColorFormatter, ErrorTracebackHandler
import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            '()': 'config.settings.log_config.ColorFormatter',
            'use_colors': False
        },
        'console': {
            '()': 'config.settings.log_config.ColorFormatter',
            'use_colors': True
        },
    },
    'filters': {
        'exclude_errors': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno < logging.ERROR
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'apps_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/apps.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
            'filters': ['exclude_errors'],
        },
        'django_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
            'filters': ['exclude_errors'],
        },
        'error_handler': {
            'level': 'ERROR',
            '()': 'config.settings.log_config.ErrorTracebackHandler',
            'base_dir': 'logs'
        }
    },
    'loggers': {
        'apps': {
            'handlers': ['console', 'apps_file', 'error_handler'],
            'level': 'INFO',
            'propagate': False,
        }, 'django': {
            'handlers': ['console', 'django_file'],
            'level': 'INFO',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['django_file'],
            'level': 'INFO',
            'propagate': False
        },
        **{logger_name: {
            'handlers': ['console', 'django_file', 'error_handler'],
            'level': 'INFO',
            'propagate': False,
        } for logger_name in ('django.request', 'django.server')},
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
}
