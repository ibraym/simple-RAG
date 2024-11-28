# Copyright (C) 2021 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from .development import *
import tempfile

_temp_dir = tempfile.TemporaryDirectory(dir=BASE_DIR, suffix="simple_rag")
BASE_DIR = _temp_dir.name

DATA_ROOT = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_ROOT, exist_ok=True)

DATASETS_ROOT = os.path.join(DATA_ROOT, "datasets")
os.makedirs(DATASETS_ROOT, exist_ok=True)

CACHE_ROOT = os.path.join(DATA_ROOT, "cache")
os.makedirs(CACHE_ROOT, exist_ok=True)

# Suppress all logs by default
for logger in LOGGING["loggers"].values():
    if isinstance(logger, dict) and "level" in logger:
        logger["level"] = "ERROR"


LOGGING["handlers"]["server_file"] = LOGGING["handlers"]["console"]
ENABLE_ENGINE = False
