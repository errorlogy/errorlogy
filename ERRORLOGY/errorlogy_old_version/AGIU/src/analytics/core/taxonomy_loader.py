"""Load and expose the unified Errorlogy taxonomy."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

# Maps `layers` JSON keys -> top-level JSON key holding structured payload (if any).
_LAYER_PAYLOAD_KEY: dict[str, str] = {
    "GT": "game_theory_patterns",
    "GT_EXT": "game_theory_patterns_extended",
    "MP_EXT": "mechanism_pathologies_extended",
    "HM": "homo_mas_interaction_pathologies",
    "METHODS": "methods_layer",
    "LΩ": "generative_topology_layer",
    "SOCIAL_MEDIA": "social_media_layer",
    "LCJ": "legal_juridical_contour_layer",
    "LBI": "betterment_improvement_layer",
    "LAC": "agent_strategy_contribution_layer",
    "LCC": "cognitive_competence_capacity_layer",
    "MAX_UNIVERSE": "max_mode_universe",
    "WMS": "weak_multisource_signal_layer",
    "ACC": "agent_contour_contribution_cluster_layer",
    "EGD": "echo_room_group_dynamics_layer",
    "FPD": "fuzzy_predictive_dynamics_layer",
    "T4D": "temporal_spatial_topology_layer",
    "CAT": "catastrophe_theory_layer",
}


class TaxonomyCounts(BaseModel):
    model_config = ConfigDict(extra="ignore")

    CB: int = 0
    SF: int = 0
    MP: int = 0
    atomic_total: int = 0
    PNO: int = 0
    GT: int = 0
    methods_modules: int = 0
    methods_total: int = 0
    CAT_modes: int = 0
    CAT_methods: int = 0
    T4D_modes: int = 0
    T4D_methods: int = 0
    FPD_methods: int = 0
    ACC_cluster_archetypes: int = 0


class TaxonomyMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str
    ontology: str
    description: str
    counts: TaxonomyCounts
    layers: dict[str, str]


class TaxonomyLoader:
    """Singleton-ish loader for the JSON taxonomy."""

    _data: dict[str, Any] | None = None

    @classmethod
    def load(cls, path: Path | None = None) -> dict[str, Any]:
        if cls._data is not None:
            return cls._data

        if path is None:
            from analytics.config import TAXONOMY_PATH

            path = TAXONOMY_PATH

        with open(path, "r", encoding="utf-8") as f:
            cls._data = json.load(f)
        return cls._data

    @classmethod
    def meta(cls) -> TaxonomyMeta:
        data = cls.load()
        return TaxonomyMeta(
            version=data.get("version", ""),
            ontology=data.get("ontology", ""),
            description=data.get("description", ""),
            counts=TaxonomyCounts(**data.get("counts", {})),
            layers=data.get("layers", {}),
        )

    @classmethod
    def layer_names(cls) -> list[str]:
        data = cls.load()
        return list(data.get("layers", {}).keys())

    @classmethod
    def get_layer(cls, name: str, *, limit: int = 200) -> dict[str, Any] | None:
        data = cls.load()
        layers = data.get("layers", {})
        key = cls._normalize_layer_name(name, layers)
        if key is None:
            return None

        limit = max(1, min(limit, 10_000))
        description = layers[key]
        payload = cls._resolve_layer_payload(data, key, limit=limit)
        return {
            "name": key,
            "description": description,
            **payload,
        }

    @staticmethod
    def _normalize_layer_name(raw: str, layers: dict[str, str]) -> str | None:
        key = raw.strip()
        if key in layers:
            return key
        upper = raw.strip().upper()
        if upper in layers:
            return upper
        return None

    @classmethod
    def _resolve_layer_payload(
        cls, data: dict[str, Any], layer_key: str, *, limit: int
    ) -> dict[str, Any]:
        """Build `data`, `truncated`, and `summary` for a taxonomy layer."""

        if layer_key in {"L1", "L2", "L3", "L4", "L5"}:
            modes = [m for m in data.get("atomic_modes", []) if m.get("layer") == layer_key]
            truncated = len(modes) > limit
            return {
                "kind": "atomic_modes",
                "data": {"atomic_modes": modes[:limit]},
                "truncated": truncated,
                "summary": {"atomic_modes_total": len(modes), "returned": min(len(modes), limit)},
            }

        if layer_key == "L6":
            comp = data.get("composite_patterns") or {}
            pno = comp.get("PNO")
            return {
                "kind": "composite_L6",
                "data": {"composite_patterns": {"PNO": pno}},
                "truncated": False,
                "summary": {
                    "pno_patterns": len(pno) if isinstance(pno, list) else 0,
                },
            }

        json_key = _LAYER_PAYLOAD_KEY.get(layer_key)
        if json_key is None:
            return {
                "kind": "description_only",
                "data": {},
                "truncated": False,
                "summary": {},
            }

        blob = data.get(json_key)
        if blob is None:
            return {
                "kind": "missing_blob",
                "data": {},
                "truncated": False,
                "summary": {"expected_key": json_key},
            }

        if isinstance(blob, list):
            truncated = len(blob) > limit
            return {
                "kind": "list",
                "data": {json_key: blob[:limit]},
                "truncated": truncated,
                "summary": {"items_total": len(blob), "returned": min(len(blob), limit)},
            }

        return {
            "kind": "object",
            "data": {json_key: blob},
            "truncated": False,
            "summary": {"payload_key": json_key},
        }
