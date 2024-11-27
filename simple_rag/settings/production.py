# Copyright (C) 2021 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from .base import *

DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("SIMPLE_RAG_POSTGRES_HOST", "db"),
        "NAME": os.getenv("SIMPLE_RAG_POSTGRES_DBNAME", "simple_rag"),
        "USER": os.getenv("SIMPLE_RAG_POSTGRES_USER", "root"),
        "PASSWORD": os.getenv("SIMPLE_RAG_POSTGRES_PASSWORD", ""),
        "PORT": os.getenv("SIMPLE_RAG_POSTGRES_PORT", 5432),
    }
}
