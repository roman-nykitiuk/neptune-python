from .base import *  # noqa: F403, F401, F405

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # noqa: F405
INTERNAL_IPS = ['127.0.0.1']
