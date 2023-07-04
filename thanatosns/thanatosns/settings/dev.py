from thanatosns.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-yt0oh!cg9wr70@bb97p$bx$b^y9_1o=i=i+m*z=297*l+#!mf_"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "thanatosns_dev",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": 5432,
        "OPTIONS": {
            # The default timeout of psql, added for modification as required.
            "connect_timeout": 30
        },
    }
}

INSTALLED_APPS = ["daphne"] + INSTALLED_APPS + ["django_extensions"]
