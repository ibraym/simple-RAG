#!/bin/sh

# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

# This is a wrapper script for running backend services. It waits for services
# the backend depends on to start before executing the backend itself.

~/wait-for-it.sh "${SIMPLE_RAG_POSTGRES_HOST}:${DASHBOARD_POSTGRES_PORT:-5432}" -t 0
~/wait-for-it.sh "${SIMPLE_RAG_QDRANT_HOST}:${SIMPLE_RAG_QDRANT_PORT}" -t 0

exec "$@"