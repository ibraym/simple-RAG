# Copyright (C) 2023 Reveal AI UG
#
# SPDX-License-Identifier: MIT

"""
ASGI config for Simple RAG project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_rag.settings.development")

application = get_asgi_application()
