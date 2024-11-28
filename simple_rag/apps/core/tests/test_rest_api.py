# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

import json
from unittest.mock import patch, MagicMock

from rest_framework.test import APITestCase
from rest_framework import status

from simple_rag.apps.core.qdrant import BaseQueryEngine

class RAGBaseAPITestCase(APITestCase):
    def setUp(self):
        self.valid_text_request = {
            'text': 'Пример текста для обработки'
        }
        self.invalid_text_request = {
            'text': ''
        }

class RAGProcessAPITestCase(RAGBaseAPITestCase):
    def _run_api_rag_process(self, data):
        response = self.client.post(
            '/api/rag/process',
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    def test_process_text_valid_request(self):
        response = self._run_api_rag_process(self.valid_text_request)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data

    def test_process_text_invalid_request(self,):
        response = self._run_api_rag_process(self.invalid_text_request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

class RAGQueryAPITestCase(RAGBaseAPITestCase):
    def _run_api_rag_query(self, data):
        response = self.client.post(
            '/api/rag/query',
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    @patch('simple_rag.apps.core.views.query_engine')
    def test_query_valid_request(self, mock_query_engine):
        mock_query_engine = MagicMock(spec=BaseQueryEngine)
        mock_query_engine.query.return_value = None
        response = self._run_api_rag_query(self.valid_text_request)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_query_invalid_request(self):
        response = self._run_api_rag_query(self.invalid_text_request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
