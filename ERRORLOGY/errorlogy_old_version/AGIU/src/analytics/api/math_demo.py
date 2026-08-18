"""Demo math endpoints for FPD, ACC, and other layers."""

from fastapi import APIRouter

from analytics.services.fuzzy_service import (
    FuzzyTrajectoryRequest,
    FuzzyTrajectoryResponse,
    compute_trajectory,
)
from analytics.services.cluster_service import (
    ClusterRequest,
    ClusterResponse,
    kmeans_cluster,
)

router = APIRouter(tags=["math-demo"])


@router.post("/math/fuzzy/trajectory", response_model=FuzzyTrajectoryResponse)
def fuzzy_trajectory(req: FuzzyTrajectoryRequest) -> FuzzyTrajectoryResponse:
    """Compute a smooth fuzzy membership trajectory (FPD layer demo)."""
    return compute_trajectory(req)


@router.post("/math/cluster/kmeans", response_model=ClusterResponse)
def cluster_kmeans(req: ClusterRequest) -> ClusterResponse:
    """Run KMeans clustering on supplied data or synthetic demo (ACC layer demo)."""
    return kmeans_cluster(req)
