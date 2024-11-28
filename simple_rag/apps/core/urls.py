# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from django.urls import path, include
from rest_framework import routers

from django.views.generic import RedirectView
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from simple_rag.apps.core.views import RAGView

router = routers.DefaultRouter(trailing_slash=False)
router.register("rag", RAGView, basename="rag")

urlpatterns = [
    # Entry point for a client
    path(
        "", RedirectView.as_view(url=settings.UI_URL, permanent=True, query_string=True)
    ),
    # documentation for API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("api/docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # entry point for API
    path("api/", include(router.urls)),
]