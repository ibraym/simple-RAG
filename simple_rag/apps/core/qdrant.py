# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from typing import List

from django.conf import settings
from qdrant_client import QdrantClient
from llama_index.core.schema import Document
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

from simple_rag.apps.core.pipeline import sparse_doc_vectors, sparse_query_vectors, pipeline

client = QdrantClient(host=settings.QDRANT_GATEWAY['HOST'], port=settings.QDRANT_GATEWAY['PORT'])

def create_vector_store(
    collection_name: str = settings.RAG_SETTINGS['VECTOR_STORE']['COLLECTION_NAME'],
    batch_size: int = settings.RAG_SETTINGS['VECTOR_STORE']['BATCH_SIZE'],
    enable_hybrid: bool = settings.RAG_SETTINGS['VECTOR_STORE']['ENABLE_HYBRID'],
):
    """
    Create a vector store for the documents.
    """
    vector_store = QdrantVectorStore(
        collection_name,
        client=client,
        batch_size=batch_size,
        enable_hybrid=enable_hybrid,
        sparse_doc_fn=sparse_doc_vectors,
        sparse_query_fn=sparse_query_vectors,
    )

    return vector_store

def create_index(documents: List[Document], vector_store: QdrantVectorStore):
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    vector_store_index = VectorStoreIndex.from_documents(
        documents,
        show_progress=True,
        transformations=pipeline,
        storage_context=storage_context,
    )

    return vector_store_index

def get_index(
    collection_name: str = settings.RAG_SETTINGS['VECTOR_STORE']['COLLECTION_NAME'],
    batch_size: int = settings.RAG_SETTINGS['VECTOR_STORE']['BATCH_SIZE'],
    enable_hybrid: bool = settings.RAG_SETTINGS['VECTOR_STORE']['ENABLE_HYBRID'],
) -> VectorStoreIndex:
    """
    Get the index from the vector store.
    """
    vector_store = create_vector_store(
        collection_name=collection_name,
        batch_size=batch_size,
        enable_hybrid=enable_hybrid,
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
    )
    return index

def create_query_engine(
    similarity_top_k: int = settings.RAG_SETTINGS['QUERY']['SIMILARITY_TOP_K'],
    sparse_top_k: int = settings.RAG_SETTINGS['QUERY']['SPARSE_TOP_K'],
) -> BaseQueryEngine:
    """
    Create a query engine.
    """
    index: VectorStoreIndex = get_index()
    query_engine: BaseQueryEngine = index.as_query_engine(
        similarity_top_k=similarity_top_k,
        sparse_top_k=sparse_top_k,
        vector_store_query_mode=settings.RAG_SETTINGS['QUERY']['MODE'],
    )
    return query_engine

def collection_exists(collection_name: str = settings.RAG_SETTINGS['VECTOR_STORE']['COLLECTION_NAME']) -> bool:
    """
    Check if a collection exists in the vector store.
    """
    collections = [collection.name for collection in client.get_collections().collections]
    return collection_name in collections
