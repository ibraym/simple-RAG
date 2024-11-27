# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

from typing import List

from pydantic import BaseModel

class TextRequest(BaseModel):
    """
    Model class for process text request.
    """
    text: str

class ProcessTextResponse(BaseModel):
    """
     Model class for process text response.
    """
    tokens: List[str]

class QueryRequest(BaseModel):
    """
    Model class for query request.
    """
    dataset: str
    text: str
    score: float

class RelevantTextResponse(BaseModel):
    """
     Model class for query results response.
    """
    results: List[QueryRequest]
