"""Taxonomy introspection endpoints."""

from fastapi import APIRouter, HTTPException

from analytics.core.taxonomy_loader import TaxonomyLoader, TaxonomyMeta

router = APIRouter(tags=["taxonomy"])


@router.get("/taxonomy/meta", response_model=TaxonomyMeta)
def taxonomy_meta() -> TaxonomyMeta:
    return TaxonomyLoader.meta()


@router.get("/taxonomy/layers")
def taxonomy_layers() -> list[str]:
    return TaxonomyLoader.layer_names()


@router.get("/taxonomy/layer/{name}")
def taxonomy_layer(name: str, limit: int = 200) -> dict:
    if limit < 1:
        limit = 1
    if limit > 10_000:
        limit = 10_000
    layer = TaxonomyLoader.get_layer(name, limit=limit)
    if layer is None:
        raise HTTPException(status_code=404, detail=f"Layer '{name}' not found")
    return layer
