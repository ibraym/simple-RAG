# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from rest_framework import serializers

from simple_rag.apps.core.models import TextRequest, ProcessTextResponse, QueryRequest

class TextRequestSerializer(serializers.Serializer):
    text = serializers.CharField()

    def validate(self, instance: TextRequest):
        if instance.text is None or instance.text == '':
            raise serializers.ValidationError('text should not be empty')
        return instance

    def to_internal_value(self, data):
        return TextRequest(text=data['text'])

    def to_representation(self, instance: TextRequest):
        data = {
            'text': instance.text
        }

        return data

class ProcessTextResponseSerializer(serializers.Serializer):
    tokens = serializers.ListField(child=serializers.CharField())

    def to_representation(self, instance: ProcessTextResponse):
        data = {
            'tokens': instance.tokens
        }

        return data

class QueryRequestSerializer(serializers.Serializer):
    dataset = serializers.CharField()
    text = serializers.CharField()
    score = serializers.FloatField()

    def to_internal_value(self, data):
        return QueryRequest(
            dataset=data['dataset'],
            text=data['text'],
            score=data['score'],
            additional_metadata=data['additional_metadata']
        )

    def to_representation(self, instance: QueryRequest):
        data = instance.model_dump(mode='json')
        return data
