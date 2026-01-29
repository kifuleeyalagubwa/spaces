"""
Django settings for classroom project
Safe for deployment on Koyeb with or without Redis
"""

import os
import socket
from pathlib import Path
import dj_database_url

# =============================================================================
# BASE DIR
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SECURITY
# =============================================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-key-only-for-local-development"
)

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

PORT = os.environ.get("PORT", 8000)

# =============================================================================
# HOSTS
# =============================================================================

try:
    LOCAL_IP = socket.gethostbyname(socket.gethostname())
except Exception:
    LOCAL_IP = "127.0.0.1"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    LOCAL_IP,
    ".koyeb.app",
    ".koyeb.tech",
]

if os.environ.get("ALLOWED_HOSTS"):
    ALLOWED_HOSTS.extend(
        [h.strip() for h in os.environ["ALLOWED_HOSTS"].split(",")]
    )


# =============================================================================
# APPLICATIONS
# =============================================================================

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "channels",

    "core",
    "study",
    "trends",
    "exams.apps.ExamsConfig",

    "phonenumber_field",
    "django_countries",
    "crispy_forms",
    "crispy_bootstrap5",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "classroom.middleware.NoCacheMiddleware",
    "trends.middleware.InstitutionMiddleware",
]


# =============================================================================
# URLS / TEMPLATES
# =============================================================================

ROOT_URLCONF = "classroom.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.environ.get("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG,
    )


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Kampala"
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC / MEDIA
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =============================================================================
# DEFAULT PK
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# AUTH
# =============================================================================

AUTH_USER_MODEL = "trends.User"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# =============================================================================
# ASGI / CHANNELS (REDIS OPTIONAL)
# =============================================================================

ASGI_APPLICATION = "classroom.asgi.application"

REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
                "capacity": 1500,
                "expiry": 10,
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }


# =============================================================================
# EXAMS (SAFE WITHOUT REDIS)
# =============================================================================

REDIS_EXAM_ATTEMPTS_PREFIX = "exam_attempt:"
REDIS_GRADING_QUEUE_KEY = "grading_queue"
REDIS_AUTO_SUBMIT_KEY = "auto_submit_tasks"

EXAM_SETTINGS = {
    "BROWSER_LEAVE_LIMIT": 3,
    "AUTO_SUBMIT_CHECK_INTERVAL": 5,
}


# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


# =============================================================================
# PRODUCTION SECURITY
# =============================================================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")