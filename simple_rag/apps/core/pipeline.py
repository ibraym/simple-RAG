# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

import re
import os
from os import path as osp
from typing import List, Sequence, Tuple

from django.conf import settings
import spacy
from llama_index.core import Settings
from llama_index.core.schema import TransformComponent, BaseNode
from llama_index.core.node_parser import TextSplitter
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

def process_text(text: str):
    """
    Process text and return normalized tokens.
    """
    doc = nlp(text)

    tokens = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop and not token.is_punct
    ]

    return tokens

def process_review(text: str):
    """
    Processes a review text and extracts specific fields.
    Args:
        text (str): The review text to be processed.
    Returns:
        dict: A dictionary containing the extracted fields 'name_ru', 'rubrics', and 'text'.
              If the input text is empty or only contains whitespace, returns None.
    Extracted Fields:
        - 'name_ru': The value following 'name_ru=' and before 'rubrics=' or 'text=' or end of string.
        - 'rubrics': The value following 'rubrics=' and before 'text=' or end of string.
        - 'text': The value following 'text=' until the end of the string.
    """

    if text.strip():
        review = {}
        name_match = re.search(r'name_ru=(.*?)(?=\srubrics=|\stext=|$)', text)
        rubrics_match = re.search(r'rubrics=(.*?)(?=\stext=|$)', text)
        text_match = re.search(r'text=(.*)', text)

        review['name_ru'] = name_match.group(1).strip() if name_match else ''
        review['rubrics'] = rubrics_match.group(1).strip() if rubrics_match else ''
        review['text'] = text_match.group(1).strip() if text_match else None

        return review

    return None

class ProcessTextTransformer(TransformComponent):
    """
    A transformer component that processes text nodes and returns normalized tokens.
    Methods
    """
    def __init__(self):
        super().__init__()

    def __call__(self, nodes: Sequence[BaseNode], **kwargs) -> Sequence[BaseNode]:
        """
        Process text and return normalized text with metadata.
        """
        processed_nodes = []
        for node in nodes:
            text = node.get_content()
            # get review parts
            review = process_review(text)
            if review is None or review['text'] == '':
                continue
            # process full review
            review_text = f"{review['name_ru']} {review['rubrics']} {review['text']}"
            tokens = process_text(review_text)
            # set content to processed tokens
            node.set_content(' '.join(tokens))
            # set metadata
            node.metadata['name_ru'] = review['name_ru']
            node.metadata['rubrics'] = review['rubrics']
            node.metadata['review_text'] = review['text']
            node.excluded_embed_metadata_keys.extend(['name_ru', 'rubrics', 'review_text', 'file_path'])
            processed_nodes.append(node)
        return processed_nodes

class CustomTextSplitter(TextSplitter):
    """
    CustomTextSplitter is a subclass of TextSplitter that splits text based on
    a specific regular expression pattern `(?=name_ru=)`.
    """
    def split_text(self, text: str) -> List[str]:
        return re.split(r'(?=name_ru=)', text)

# create the pipeline with transformations
pipeline = [
    CustomTextSplitter(),
    ProcessTextTransformer(),
]

def sparse_doc_vectors(
    texts: List[str],
) -> Tuple[List[List[int]], List[List[float]]]:
    """
    Compute sparse document vectors using TF-IDF.
    To be used by VectorStoreIndex.
    """
    tfidf_matrix = vectorizer.fit_transform(texts)

    # cache the vectorizer
    joblib.dump(vectorizer, vectorizer_cache_path)

    indices = []
    values = []
    for i in range(len(texts)):
        cuu_indices = tfidf_matrix[i,:].nonzero()[1]
        values.append([tfidf_matrix[i, x] for x in cuu_indices])
        indices.append(cuu_indices)

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

