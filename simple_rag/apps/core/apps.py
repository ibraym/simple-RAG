# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'simple_rag.apps.core'

    def ready(self):
        # Required to define signals in application
        pass