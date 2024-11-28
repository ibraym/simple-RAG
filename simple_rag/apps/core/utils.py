# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

import os
from os import path as osp
import hashlib
from typing import List, Dict

import joblib
from pydantic import BaseModel
from django.conf import settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

class DocumentInfo(BaseModel):
    mtime: float
    hash: str

def list_documents(base_path: str) -> List[Document]:
    """
    List all documents based on DATASET_EXTS settings.
    """
    documents = SimpleDirectoryReader(
        base_path,
        required_exts=['.txt'],#settings.RAG_SETTINGS['DATASET_EXTS'],
        filename_as_id=True
    ).load_data(show_progress=True)

    return documents

def get_file_info(file_path: str) -> DocumentInfo:
    """
    Retrieves the modification time and hash of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        dict: A dictionary containing:
            - 'mtime': Modification time (float).
            - 'hash': SHA256 hash of the file content (str).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get modification time
    mtime = os.path.getmtime(file_path)

    # Compute SHA256 hash
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()

    return DocumentInfo(mtime=mtime, hash=file_hash)

def is_file_changed(current_info: DocumentInfo, previous_info: DocumentInfo=None) -> bool:
    """
    Checks if a file has changed based on its information.

    Args:
        current_info (dict): Current file information with 'mtime' and 'hash'.
        previous_info (dict): Previous file information with keys:
            - 'mtime': Modification time (float).
            - 'hash': SHA256 hash of the file (str).

    Returns:
        tuple: (changed (bool), current_info (dict))
            - changed: True if the file has changed, False otherwise.
            - current_info: Current file information with 'mtime' and 'hash'.
    """

    if previous_info is None:
        return True
    # Check if mtime or hash has changed
    if current_info.mtime != previous_info.mtime or current_info.hash != previous_info.hash:
        return True
    # No changes detected
    return False

def build_documents_info_index(documents: List[Document]) -> Dict[str, DocumentInfo]:
    """
    Builds an index of document information from a list of documents.

    Args:
        documents (List[Document]): A list of Document objects.

    Returns:
        Dict[str, DocumentInfo]: A dictionary where the keys are document IDs and the values are DocumentInfo objects.
    """
    infos: List[DocumentInfo] = {}
    for document in documents:
        file_path = document.metadata['file_path']
        infos[file_path] = get_file_info(file_path)
    return infos

def build_and_cache_documents_info(cache_path: str, documents: List[Document]):
    infos: Dict[str, DocumentInfo] = build_documents_info_index(documents)
    joblib.dump(infos, cache_path)

def filter_documents(documents: List[Document], cache_path: str) -> List[Document]:
    if osp.exists(cache_path):
        old_infos: Dict[str, DocumentInfo] = joblib.load(cache_path)
        # filter new documents
        new_documents = []
        for document in documents:
            file_path = document.metadata['file_path']
            if file_path in old_infos.keys():
                info = get_file_info(file_path)
                if is_file_changed(info, old_infos[file_path]):
                    new_documents.append(document)
            else:
                new_documents.append(document)
    else:
        new_documents = documents
    # rebuild cache
    build_and_cache_documents_info(cache_path, documents)

    return new_documents



