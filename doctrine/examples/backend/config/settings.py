"""One small settings file keeps the example readable.

A real project splits this into base, local and production profiles selected by one
environment variable (BE-CFG-1), reads every value from the environment (BE-EXT-3),
and makes the production profile refuse to boot on unsafe values (BE-CFG-2).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ROOT_URLCONF = "config.urls"
# BE-API-8: timestamps are timezone-aware and stored in UTC.
USE_TZ = True
TIME_ZONE = "UTC"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "rest_framework.authtoken",
    "accounts",
    "teams",
    "invitations",
]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware"]
AUTH_USER_MODEL = "accounts.User"
# No SECRET_KEY: nothing here signs anything, and a repository never holds one (BE-CFG-3).

# SQLite so the example needs no services. Run transaction and constraint tests on the
# production engine before trusting them (T-8).
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"},
}

REST_FRAMEWORK = {
    # BE-API-5: deny by default. A public endpoint opts out through PublicAPIView.
    "DEFAULT_AUTHENTICATION_CLASSES": ["accounts.authentication.BearerAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # BE-API-2: one handler builds every error body.
    "EXCEPTION_HANDLER": "common.views.api_exception_handler",
}
