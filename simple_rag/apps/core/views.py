# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view, extend_schema
)

from simple_rag.apps.core.models import TextRequest, ProcessTextResponse
from simple_rag.apps.core.serializers import TextRequestSerializer, ProcessTextResponseSerializer, QueryRequestSerializer, QueryRequest
from simple_rag.apps.core.pipeline import process_text
from simple_rag.apps.core.qdrant import create_query_engine

query_engine = create_query_engine()

@extend_schema(tags=['rag'])
@extend_schema_view(
    process=extend_schema(
        summary='Process text and return normalized tokens',
        request=TextRequestSerializer,
        responses={
            200: ProcessTextResponseSerializer,
        }
    ),
    query=extend_schema(
        summary='Search fo top 3 most relevant texts from vector database',
        request=TextRequestSerializer,
        responses={
            200: QueryRequestSerializer(many=True),
        }
    ),
)
class RAGView(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def process(self, request) -> Response:
        """
        Process text and return normalized tokens.
        """
        try:
            request_serializer = TextRequestSerializer(data=request.data)
            request_serializer.is_valid(raise_exception=True)
            request: TextRequest = request_serializer.validated_data
            tokens = process_text(request.text)
            serializer = ProcessTextResponseSerializer(
                ProcessTextResponse(
                    tokens=tokens
            ))
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def query(self, request) -> Response:
        """
        Search fo top 3 most relevant texts from vector database.
        """
        try:
            request_serializer = TextRequestSerializer(data=request.data)
            request_serializer.is_valid(raise_exception=True)
            request: TextRequest = request_serializer.validated_data
            response = query_engine.query(
                ' '.join(process_text(request.text)),
            )
            data = []
            for node in response.source_nodes:
                data.append(QueryRequest(
                    dataset=node.metadata['file_name'],
                    text=node.metadata['review_text'],
                    additional_metadata={
                        'name_ru': node.metadata['name_ru'],
                        'rubrics': node.metadata['rubrics'],
                    },
                    score=node.get_score()
                ))
            serializer = QueryRequestSerializer(
                data, many=True
            )
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
