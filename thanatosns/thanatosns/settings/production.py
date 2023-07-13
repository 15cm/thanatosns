from thanatosns.settings.base import *

SECRET_KEY = os.getenv("THANATOSNS_DJANGO_SECRET_KEY", None)

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Django CSRF doesn't work well behind https reverse proxy.
if host_url := os.getenv("THANATOSNS_HOST_URL", None):
    CSRF_TRUSTED_ORIGINS = [host_url]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "normal": {"format": ("[%(asctime)s] [%(levelname)s] %(message)s")},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "normal"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}
