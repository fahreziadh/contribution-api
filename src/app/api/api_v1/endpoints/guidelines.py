# Copyright (C) 2023, Quack AI.

# All rights reserved.
# Copying and/or distributing is strictly prohibited without the express permission of its copyright owner.

from datetime import datetime
from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_current_user, get_guideline_crud, get_repo_crud
from app.crud import GuidelineCRUD, RepositoryCRUD
from app.models import Guideline, Repository, UserScope
from app.schemas.guidelines import ContentUpdate, GuidelineCreate, GuidelineEdit, OrderUpdate

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_guideline(
    payload: GuidelineCreate,
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    _=Security(get_current_user, scopes=[UserScope.USER, UserScope.ADMIN]),
) -> Guideline:
    return await guidelines.create(payload)


@router.get("/{guideline_id}", status_code=status.HTTP_200_OK)
async def get_guideline(
    guideline_id: int = Path(..., gt=0),
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    _=Security(get_current_user, scopes=[UserScope.USER, UserScope.ADMIN]),
) -> Guideline:
    return cast(Guideline, await guidelines.get(guideline_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK)
async def fetch_guidelines(
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    _=Security(get_current_user, scopes=[UserScope.ADMIN]),
) -> List[Guideline]:
    return [elt for elt in await guidelines.fetch_all()]


@router.get("/from/{repo_id}", status_code=status.HTTP_200_OK)
async def fetch_guidelines_from_repo(
    repo_id: int = Path(..., gt=0),
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    repos: RepositoryCRUD = Depends(get_repo_crud),
    user=Security(get_current_user, scopes=[UserScope.ADMIN, UserScope.USER]),
) -> List[Guideline]:
    if user.scope == UserScope.USER and user.id != cast(Repository, await repos.get(repo_id, strict=True)).owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your user scope is not compatible with this operation.",
        )
    return [elt for elt in await guidelines.fetch_all(("repo_id", repo_id))]


@router.put("/{guideline_id}", status_code=status.HTTP_200_OK)
async def update_guideline_content(
    payload: GuidelineEdit,
    guideline_id: int = Path(..., gt=0),
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    _=Security(get_current_user, scopes=[UserScope.USER, UserScope.ADMIN]),
) -> Guideline:
    return await guidelines.update(guideline_id, ContentUpdate(**payload.dict(), updated_at=datetime.utcnow()))


@router.put("/{guideline_id}/order/{order_idx}", status_code=status.HTTP_200_OK)
async def update_guideline_order(
    guideline_id: int = Path(..., gt=0),
    order_idx: int = Path(..., gte=0),
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    _=Security(get_current_user, scopes=[UserScope.USER, UserScope.ADMIN]),
) -> Guideline:
    return await guidelines.update(guideline_id, OrderUpdate(order=order_idx, updated_at=datetime.utcnow()))


@router.delete("/{guideline_id}", status_code=status.HTTP_200_OK)
async def delete_guideline(
    guideline_id: int = Path(..., gt=0),
    guidelines: GuidelineCRUD = Depends(get_guideline_crud),
    _=Security(get_current_user, scopes=[UserScope.USER, UserScope.ADMIN]),
) -> None:
    await guidelines.delete(guideline_id)