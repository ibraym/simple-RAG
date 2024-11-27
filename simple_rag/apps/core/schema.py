# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

import re

from drf_spectacular.openapi import AutoSchema
from rest_framework import serializers

class CustomAutoSchema(AutoSchema):
    def get_operation_id(self):
        # Change style of operation ids to [viewset _ action _ object]
        # This form is simpler to handle during SDK generation

        tokenized_path = self._tokenize_path()
        # replace dashes as they can be problematic later in code generation
        tokenized_path = [t.replace('-', '_') for t in tokenized_path]

        if self.method == 'GET' and self._is_list_view():
            action = 'list'
        else:
            action = self.method_mapping[self.method.lower()]

        if not tokenized_path:
            tokenized_path.append('root')

        if re.search(r'<drf_format_suffix\w*:\w+>', self.path_regex):
            tokenized_path.append('formatted')

        return '_'.join([tokenized_path[0]] + [action] + tokenized_path[1:])

    def _get_request_for_media_type(self, serializer, *args, **kwargs):
        # Enables support for required=False serializers in request body specification
        # in drf-spectacular. Doesn't block other extensions on the target serializer.
        # This is supported by OpenAPI and by SDK generator, but not by drf-spectacular

        schema, required = super()._get_request_for_media_type(serializer, *args, **kwargs)

        if isinstance(serializer, serializers.Serializer):
            if not serializer.required:
                required = False

        return schema, required