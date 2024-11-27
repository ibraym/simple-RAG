# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from rest_framework.renderers import JSONRenderer


class SimpleRagAPIRenderer(JSONRenderer):
    media_type = 'application/vnd.simple_rag+json'