"""Deterministic analytics engine for Errorlogy MAS."""

from . import fuzzy, alpha, wms, pno, acc, egd, t4d, cat, fpd, guards

ENGINE_VERSION = "v1-math"

__all__ = [
    "ENGINE_VERSION",
    "fuzzy",
    "alpha",
    "wms",
    "pno",
    "acc",
    "egd",
    "t4d",
    "cat",
    "fpd",
    "guards",
]
