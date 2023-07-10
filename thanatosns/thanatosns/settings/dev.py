from thanatosns.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-yt0oh!cg9wr70@bb97p$bx$b^y9_1o=i=i+m*z=297*l+#!mf_"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


INSTALLED_APPS = ["daphne"] + INSTALLED_APPS
