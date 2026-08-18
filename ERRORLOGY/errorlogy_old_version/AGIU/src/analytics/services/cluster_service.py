"""Agent / Contour Contribution Clusters (ACC) demonstrations."""

import numpy as np
from pydantic import BaseModel
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class ClusterRequest(BaseModel):
    n_clusters: int = 3
    random_state: int = 42
    data: list[list[float]] | None = None


class ClusterResponse(BaseModel):
    labels: list[int]
    centers: list[list[float]]
    inertia: float


def kmeans_cluster(req: ClusterRequest) -> ClusterResponse:
    if req.data is None:
        # Demo: 3 synthetic 2D blobs
        rng = np.random.default_rng(req.random_state)
        blobs = []
        for center in [(0, 0), (5, 5), (-4, 6)]:
            blobs.append(rng.normal(loc=center, scale=1.0, size=(30, 2)))
        X = np.vstack(blobs)
    else:
        X = np.array(req.data, dtype=float)

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=req.n_clusters, random_state=req.random_state, n_init="auto")
    labels = kmeans.fit_predict(Xs)

    # Return centers in original scale
    centers_orig = scaler.inverse_transform(kmeans.cluster_centers_)

    return ClusterResponse(
        labels=labels.tolist(),
        centers=centers_orig.tolist(),
        inertia=float(kmeans.inertia_),
    )
