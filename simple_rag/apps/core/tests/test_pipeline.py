# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from simple_rag.apps.core.pipeline import (process_text, process_review,
    sparse_doc_vectors, sparse_query_vectors)

def test_process_text():
    text = 'Пример текста для обработки'
    tokens = process_text(text)
    assert isinstance(tokens, list)
    assert all(isinstance(token, str) for token in tokens)
    assert tokens == ['пример', 'текст', 'обработка']

def test_process_review():
    text = 'name_ru=Пример rubrics=Тест text=Это пример текста для обработки'
    review = process_review(text)
    assert isinstance(review, dict)
    assert review['name_ru'] == 'Пример'
    assert review['rubrics'] == 'Тест'
    assert review['text'] == 'Это пример текста для обработки'

    empty_text = ''
    review = process_review(empty_text)
    assert review is None

def test_sparse_doc_vectors():
    texts = ['Пример текста для обработки', 'Еще один пример текста']
    indices, values = sparse_doc_vectors(texts)
    assert isinstance(indices, list)
    assert isinstance(values, list)
    assert all(isinstance(index_list, list) for index_list in indices)
    assert all(isinstance(value_list, list) for value_list in values)

def test_sparse_query_vectors():
    texts = ['Пример текста для обработки', 'Еще один пример текста']
    indices, values = sparse_query_vectors(texts)
    assert isinstance(indices, list)
    assert isinstance(values, list)
    assert all(isinstance(index_list, list) for index_list in indices)
    assert all(isinstance(value_list, list) for value_list in values)
