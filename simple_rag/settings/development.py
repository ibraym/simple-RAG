# Copyright (C) 2021 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from .base import *
import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += [
    "django_extensions",
]

ALLOWED_HOSTS.append(get_ip())

QDRANT_GATEWAY["HOST"] = 'localhost'
QDRANT_GATEWAY["PORT"] = 6333

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Cross-Origin Resource Sharing settings for UI
UI_SCHEME = os.environ.get("UI_SCHEME", "http")
UI_HOST = os.environ.get("UI_HOST", "localhost")
UI_PORT = os.environ.get("UI_PORT", 3000)
CORS_ALLOW_CREDENTIALS = True
UI_URL = "{}://{}".format(UI_SCHEME, UI_HOST)

if UI_PORT and UI_PORT != '80':
    UI_URL += ':{}'.format(UI_PORT)

CSRF_TRUSTED_ORIGINS = [UI_URL]

CORS_ORIGIN_WHITELIST = [UI_URL]
