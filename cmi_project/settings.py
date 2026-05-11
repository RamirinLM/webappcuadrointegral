import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env(name: str, default=None):
    return os.environ.get(name, default)


def env_bool(name: str, default: bool) -> bool:
    value = env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}

SECRET_KEY = env("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required")

DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = [host.strip() for host in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if host.strip()]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'projects',
    'stakeholders',
    'resources',
    'risks',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'projects.middleware.DatabaseSchemaGuardMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cmi_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'projects.context_processors.app_shell',
            ],
        },
    },
]

WSGI_APPLICATION = 'cmi_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASE_ENGINE = env("DJANGO_DB_ENGINE", "django.db.backends.sqlite3")
DATABASE_NAME = env("DJANGO_DB_NAME", str(BASE_DIR / "db.sqlite3"))

DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": DATABASE_NAME,
        "USER": env("DJANGO_DB_USER", ""),
        "PASSWORD": env("DJANGO_DB_PASSWORD", ""),
        "HOST": env("DJANGO_DB_HOST", ""),
        "PORT": env("DJANGO_DB_PORT", ""),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", "es-ec")

TIME_ZONE = env("DJANGO_TIME_ZONE", "America/Guayaquil")

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email settings
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("DJANGO_EMAIL_HOST", "localhost")
EMAIL_PORT = int(env("DJANGO_EMAIL_PORT", "25"))
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_USE_TLS", False)
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", "no-reply@celica.local")

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", True)
CSRF_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", True)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "projects": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", "INFO")},
        "reports": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", "INFO")},
        "django.request": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", "INFO"), "propagate": False},
    },
}
