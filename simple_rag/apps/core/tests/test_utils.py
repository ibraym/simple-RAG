# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

import os
import hashlib
import tempfile
from unittest import TestCase
from unittest.mock import patch, MagicMock
from simple_rag.apps.core.utils import (list_documents, get_file_info, is_file_changed, build_documents_info_index,
    build_and_cache_documents_info, filter_documents, DocumentInfo)
from llama_index.core.schema import Document

class TestUtils(TestCase):

    @patch('simple_rag.apps.core.utils.SimpleDirectoryReader')
    def test_list_documents(self, MockSimpleDirectoryReader):
        mock_reader = MockSimpleDirectoryReader.return_value
        mock_reader.load_data.return_value = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        documents = list_documents('/fake/path')

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].get_doc_id(), '1')
        mock_reader.load_data.assert_called_once_with(show_progress=True)

    def test_get_file_info(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file_path = temp_file.name

        expected_mtime = os.path.getmtime(temp_file_path)
        expected_hash = hashlib.sha256(b"test content").hexdigest()

        file_info = get_file_info(temp_file_path)

        self.assertEqual(file_info.mtime, expected_mtime)
        self.assertEqual(file_info.hash, expected_hash)

        os.remove(temp_file_path)

    def test_is_file_changed(self):
        current_info = DocumentInfo(mtime=1000.0, hash='abc123')
        previous_info = DocumentInfo(mtime= 900.0, hash='abc123')

        self.assertTrue(is_file_changed(current_info, previous_info))

        previous_info = DocumentInfo(mtime= 1000.0, hash='def456')

        self.assertTrue(is_file_changed(current_info, previous_info))

        previous_info = DocumentInfo(mtime= 1000.0, hash='abc123')

        self.assertFalse(is_file_changed(current_info, previous_info))

    @patch('simple_rag.apps.core.utils.get_file_info')
    def test_build_documents_info_index(self, mock_get_file_info):
        mock_get_file_info.return_value = MagicMock(mtime=1000.0, hash='abc123')
        documents = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        infos = build_documents_info_index(documents)

        self.assertIn('test.txt', infos)
        self.assertEqual(infos['test.txt'].mtime, 1000.0)
        self.assertEqual(infos['test.txt'].hash, 'abc123')

    @patch('simple_rag.apps.core.utils.build_documents_info_index')
    @patch('simple_rag.apps.core.utils.joblib.dump')
    def test_build_and_cache_documents_info(self, mock_dump, mock_build_documents_info_index):
        return_value = {'test.txt': MagicMock(mtime=1000.0, hash='abc123')}
        mock_build_documents_info_index.return_value = return_value
        documents = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            cache_path = temp_file.name

        build_and_cache_documents_info(cache_path, documents)

        mock_dump.assert_called_once_with(return_value, cache_path)
        os.remove(cache_path)

    @patch('simple_rag.apps.core.utils.get_file_info')
    @patch('simple_rag.apps.core.utils.joblib.load')
    @patch('simple_rag.apps.core.utils.build_and_cache_documents_info')
    def test_filter_documents(self, mock_build_and_cache_documents_info, mock_load, mock_get_file_info):
        mock_load.return_value = {'test.txt': MagicMock(mtime=1000.0, hash='abc123')}
        mock_get_file_info.return_value = MagicMock(mtime=1000.0, hash='def456')
        documents = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            cache_path = temp_file.name

        new_documents = filter_documents(documents, cache_path)

        self.assertEqual(len(new_documents), 1)
        self.assertEqual(new_documents[0].get_doc_id(), '1')
        mock_build_and_cache_documents_info.assert_called_once_with(cache_path, documents)
        os.remove(cache_path)

    @patch('simple_rag.apps.core.utils.get_file_info')
    @patch('simple_rag.apps.core.utils.joblib.load')
    @patch('simple_rag.apps.core.utils.build_and_cache_documents_info')
    def test_filter_documents_no_cache(self, mock_build_and_cache_documents_info, mock_load, mock_get_file_info):
        mock_load.return_value = {}
        mock_get_file_info.return_value = MagicMock(mtime=1000.0, hash='abc123')
        documents = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            cache_path = temp_file.name

        new_documents = filter_documents(documents, cache_path)

        self.assertEqual(len(new_documents), 1)
        self.assertEqual(new_documents[0].get_doc_id(), '1')
        mock_build_and_cache_documents_info.assert_called_once_with(cache_path, documents)
        os.remove(cache_path)

    @patch('simple_rag.apps.core.utils.get_file_info')
    @patch('simple_rag.apps.core.utils.joblib.load')
    @patch('simple_rag.apps.core.utils.build_and_cache_documents_info')
    def test_filter_documents_with_cache_no_change(self, mock_build_and_cache_documents_info, mock_load, mock_get_file_info):
        mock_load.return_value = {'test.txt': MagicMock(mtime=1000.0, hash='abc123')}
        mock_get_file_info.return_value = MagicMock(mtime=1000.0, hash='abc123')
        documents = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            cache_path = temp_file.name

        new_documents = filter_documents(documents, cache_path)

        self.assertEqual(len(new_documents), 0)
        mock_build_and_cache_documents_info.assert_called_once_with(cache_path, documents)
        os.remove(cache_path)

    @patch('simple_rag.apps.core.utils.get_file_info')
    @patch('simple_rag.apps.core.utils.joblib.load')
    @patch('simple_rag.apps.core.utils.build_and_cache_documents_info')
    def test_filter_documents_with_cache_with_change(self, mock_build_and_cache_documents_info, mock_load, mock_get_file_info):
        mock_load.return_value = {'test.txt': MagicMock(mtime=1000.0, hash='abc123')}
        mock_get_file_info.return_value = MagicMock(mtime=1000.0, hash='def456')
        documents = [Document(doc_id='1', text='test', metadata={'file_path': 'test.txt'})]

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            cache_path = temp_file.name

        new_documents = filter_documents(documents, cache_path)

        self.assertEqual(len(new_documents), 1)
        self.assertEqual(new_documents[0].get_doc_id(), '1')
        mock_build_and_cache_documents_info.assert_called_once_with(cache_path, documents)
        os.remove(cache_path)