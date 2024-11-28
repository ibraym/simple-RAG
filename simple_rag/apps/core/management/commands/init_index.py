# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from os import path as osp

from django.conf import settings
from django.core.management.base import BaseCommand
from django.conf import settings


from simple_rag.apps.core.qdrant import collection_exists, create_vector_store, create_index, get_index
from simple_rag.apps.core.utils import list_documents, filter_documents

class Command(BaseCommand):
    help = 'Build index for all documents'

    def handle(self, *args, **options):
        if not settings.ENABLE_ENGINE:
            return None
        try:
            self.stdout.write(self.style.NOTICE('Starting to build index for all documents...'))
            documents = list_documents(settings.DATASETS_ROOT)
            if not documents or len(documents) == 0:
                self.stdout.write(self.style.ERROR('No documents found.'))
                return
            if (collection_exists()):
                # filter out not changed documents
                cache_path = osp.join(settings.CACHE_ROOT, 'doc_info.pkl')
                documents = filter_documents(documents, cache_path)
                if not documents or len(documents) == 0:
                    self.stdout.write(self.style.ERROR('No changed documents found.'))
                    return
                # refresh index
                index = get_index()
                refreshed_docs = index.refresh_ref_docs(documents)
                if refreshed_docs[0] and refreshed_docs[-1]:
                    self.stdout.write(self.style.SUCCESS('Index refreshed successfully.'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to refresh index.'))
            else:
                vector_store = create_vector_store()
                create_index(documents, vector_store)
                self.stdout.write(self.style.SUCCESS('Index created successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
            raise e
