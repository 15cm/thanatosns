from thanatosns.settings.base import *

SECRET_KEY = os.getenv("THANATOSNS_DJANGO_SECRET_KEY", None)

DEBUG = False
