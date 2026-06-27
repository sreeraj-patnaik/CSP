"""Development settings — verbose, with debug toolbar and SQLite fallback."""
from .base import *  # noqa

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Use console email in development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use local filesystem cache in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Allow all CORS in dev
CORS_ALLOW_ALL_ORIGINS = True

# Disable WhiteNoise manifest in dev (faster reloads)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
