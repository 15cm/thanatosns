from pathlib import Path
import os
from typing import Optional

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _get_int_env(name: str, default=None) -> Optional[int]:
    val = os.getenv(name)
    return int(val) if val else default


THANATOSNS_REDIS_URL = os.getenv("THANATOSNS_REDIS_URL", "redis://127.0.0.1:6379")
THANATOSNS_DB_HOST = os.getenv("THANATOSNS_DB_HOST", "localhost")
THANATOSNS_DB_PORT = os.getenv("THANATOSNS_DB_PORT", "5432")
THANATOSNS_DB_USER = os.getenv("THANATOSNS_DB_USER", "postgres")
THANATOSNS_DB_PASSWORD = os.getenv("THANATOSNS_DB_PASSWORD", "postgres")
THANATOSNS_DB_NAME = os.getenv("THANATOSNS_DB_NAME", "thanatosns")
THANATOSNS_EXPORT_DIR = os.getenv("THANATOSNS_EXPORT_DIR", "/tmp/thanatosns")
THANATOSNS_MEDIA_CONTENT_TYPES = os.getenv(
    "THANATOSNS_MEDIA_CONTENT_TYPES",
    "image/jpeg,image/png,image/gif,image/webp,video/mpeg,video/mp4,video/webm",
).split(",")
THANATOSNS_MEDIA_EXPORT_TIMEOUT = _get_int_env("THANATOSNS_MEDIA_EXPORT_TIMEOUT")
THANATOSNS_CELERY_TASK_TIME_LIMIT = _get_int_env(
    "THANATOSNS_CELERY_TASK_TIME_LIMIT", 10 * 60
)
THANATOSNS_CELERY_WORKER_CONCURRENCY = _get_int_env(
    "THANATOSNS_CELERY_WORKER_CONCURRENCY", 8
)


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "posts",
    "export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "thanatosns.urls"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ASGI_APPLICATION = "thanatosns.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": THANATOSNS_DB_NAME,
        "USER": THANATOSNS_DB_USER,
        "PASSWORD": THANATOSNS_DB_PASSWORD,
        "HOST": THANATOSNS_DB_HOST,
        "PORT": THANATOSNS_DB_PORT,
        "OPTIONS": {
            # The default timeout of psql, added for modification as required.
            "connect_timeout": 30
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{THANATOSNS_REDIS_URL}/0",
    }
}

CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = THANATOSNS_CELERY_TASK_TIME_LIMIT
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_CONCURRENCY = THANATOSNS_CELERY_WORKER_CONCURRENCY
CELERY_BROKER_URL = f"{THANATOSNS_REDIS_URL}/1"
CELERY_RESULT_BACKEND = f"{THANATOSNS_REDIS_URL}/2"
