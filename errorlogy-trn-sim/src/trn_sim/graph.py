import numpy as np


def make_ring_lattice(N: int, k_neighbors: int) -> np.ndarray:
    """Create row-normalized ring-lattice weight matrix."""
    W = np.zeros((N, N), dtype=float)
    half = max(1, k_neighbors // 2)
    for i in range(N):
        for d in range(1, half + 1):
            W[i, (i - d) % N] = 1.0
            W[i, (i + d) % N] = 1.0
    return normalize_rows(W)


def make_watts_strogatz(N: int, k_neighbors: int, rewiring_p: float, rng: np.random.Generator) -> np.ndarray:
    """Simple undirected Watts-Strogatz-like graph, returned as row-normalized W."""
    A = np.zeros((N, N), dtype=float)
    half = max(1, k_neighbors // 2)

    for i in range(N):
        for d in range(1, half + 1):
            j = (i + d) % N
            A[i, j] = 1.0
            A[j, i] = 1.0

    # Rewire only clockwise edges to avoid duplicate rewiring.
    for i in range(N):
        for d in range(1, half + 1):
            j = (i + d) % N
            if rng.random() < rewiring_p:
                A[i, j] = 0.0
                A[j, i] = 0.0
                candidates = np.where((A[i] == 0.0) & (np.arange(N) != i))[0]
                if len(candidates) > 0:
                    new_j = int(rng.choice(candidates))
                    A[i, new_j] = 1.0
                    A[new_j, i] = 1.0
    return normalize_rows(A)


def make_erdos_renyi(N: int, k_neighbors: int, rng: np.random.Generator) -> np.ndarray:
    p = min(1.0, k_neighbors / max(1, N - 1))
    upper = rng.random((N, N)) < p
    A = np.triu(upper.astype(float), 1)
    A = A + A.T
    return normalize_rows(A)


def normalize_rows(W: np.ndarray) -> np.ndarray:
    W = W.copy().astype(float)
    row_sum = W.sum(axis=1, keepdims=True)
    isolated = (row_sum[:, 0] == 0.0)
    if np.any(isolated):
        # Self-loop for isolated nodes to prevent division by zero.
        W[isolated, isolated] = 1.0
        row_sum = W.sum(axis=1, keepdims=True)
    return W / row_sum


def make_graph_matrix(graph_type: str, N: int, k_neighbors: int, rewiring_p: float, rng: np.random.Generator) -> np.ndarray:
    if graph_type == "ring_lattice":
        return make_ring_lattice(N, k_neighbors)
    if graph_type == "watts_strogatz":
        return make_watts_strogatz(N, k_neighbors, rewiring_p, rng)
    if graph_type == "erdos_renyi":
        return make_erdos_renyi(N, k_neighbors, rng)
    raise ValueError(f"Unknown graph_type: {graph_type}")
