# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from typing import List

from django.conf import settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

def list_documents(base_path: str) -> List[Document]:
    """
    List all documents based on DATASET_EXTS settings.
    """
    documents = SimpleDirectoryReader(
        base_path,
        required_exts=settings.RAG_SETTINGS['DATASET_EXTS'],
        filename_as_id=True
    ).load_data(show_progress=True)

    return documents
