# Copyright (C) 2023-2024, Quack AI.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel, Field

from .base import OptionalGHToken

__all__ = ["GuidelineCreate", "GuidelineEdit", "ContentUpdate", "OrderUpdate"]


class TextContent(BaseModel):
    content: str = Field(..., min_length=10)


class ExampleRequest(TextContent):
    language: str = Field("python", min_length=1, max_length=20)


class GuidelineExample(BaseModel):
    positive: str = Field(
        ..., min_length=3, description="a minimal code snippet where the instruction was correctly followed."
    )
    negative: str = Field(
        ..., min_length=3, description="the same snippet with minimal modifications that invalidates the instruction."
    )


class GuidelineContent(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    details: str = Field(..., min_length=6, max_length=1000)


class ParsedGuideline(GuidelineContent):
    repo_id: int = Field(..., gt=0)
    source: str


class GuidelineLocation(BaseModel):
    repo_id: int = Field(..., gt=0)
    order: int = Field(0, ge=0, nullable=False)


class GuidelineEdit(GuidelineContent, OptionalGHToken):
    pass


class GuidelineCreate(GuidelineEdit, GuidelineLocation):
    pass


class GuidelineCreation(GuidelineContent, GuidelineLocation):
    pass


class ContentUpdate(GuidelineContent):
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class OrderUpdate(OptionalGHToken):
    order: int = Field(..., ge=0, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
