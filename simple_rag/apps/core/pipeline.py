# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

import os
from os import path as osp
from typing import List, Sequence, Tuple

from django.conf import settings
import spacy
from llama_index.core import Settings
from llama_index.core.schema import TransformComponent, BaseNode
from llama_index.core.node_parser import SentenceSplitter
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from django.conf import settings

# cache nlp object
nlp = spacy.load('ru_core_news_sm')

vectorizer_cache_path = osp.join(settings.CACHE_ROOT, 'vectorizer_cache.pkl')
# Check if the vectorizer is already cached
if os.path.exists(vectorizer_cache_path):
    vectorizer = joblib.load(vectorizer_cache_path)
else:
    vectorizer = TfidfVectorizer()

Settings.embed_model = settings.RAG_SETTINGS['EMBED_MODEL']
Settings.llm = settings.RAG_SETTINGS['LLM']

def process_text(text: str) -> List[str]:
    """
    Process text and return normalized tokens.
    """
    doc = nlp(text)

    tokens: List[str] = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop and not token.is_punct
    ]

    return tokens

class ProcessTextTransformer(TransformComponent):
    """
    A transformer component that processes text nodes and returns normalized tokens.
    Methods
    """
    def __init__(self):
        super().__init__()

    def __call__(self, nodes: Sequence[BaseNode], **kwargs) -> Sequence[BaseNode]:
        """
        Process text and return normalized tokens.
        """
        for node in nodes:
            text = node.get_content()
            tokens = process_text(text)
            node.set_content(' '.join(tokens))
            node.metadata['original_text'] = text
        return nodes

def sparse_doc_vectors(
    texts: List[str],
) -> Tuple[List[List[int]], List[List[float]]]:
    """
    Compute sparse document vectors using TF-IDF.
    To be used by VectorStoreIndex.
    """
    # remove metadata
    text_cleaned = [
        ' '.join(text.split('\n\n')[1:])
        for text in texts
    ]
    # compute tf-idf
    tfidf_matrix = vectorizer.fit_transform(text_cleaned)

    # cache the vectorizer
    joblib.dump(vectorizer, vectorizer_cache_path)

    indices = []
    values = []
    for i in range(len(text_cleaned)):
        curr_indices = tfidf_matrix[i,:].nonzero()[1]
        values.append([tfidf_matrix[i, x] for x in curr_indices])
        indices.append(curr_indices)

    return indices, values

def sparse_query_vectors(
    texts: List[str],
) -> Tuple[List[List[int]], List[List[float]]]:
    """
    Compute sparse query vectors using TF-IDF.
    To be used by VectorStoreIndex.
    """
    tfidf_matrix = vectorizer.transform(texts)
    indices = []
    values = []
    for i in range(len(texts)):
        cuu_indices = tfidf_matrix[i,:].nonzero()[1]
        values.append([tfidf_matrix[i, x] for x in cuu_indices])
        indices.append(cuu_indices)

    return indices, values

# create the pipeline with transformations
pipeline = [
    SentenceSplitter(
        chunk_size=settings.RAG_SETTINGS['CHUNK_SIZE'],
        chunk_overlap=settings.RAG_SETTINGS['CHUNK_OVERLAP'],
    ),
    ProcessTextTransformer(),
]
