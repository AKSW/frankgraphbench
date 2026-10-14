"""Shared device selection for the PyTorch-based recommender models.

Replaces the previous TensorFlow ``ConfigProto``/``Session`` device handling.
``resolve_device`` prefers a CUDA GPU, then an Apple Silicon (MPS) accelerator,
and finally falls back to the CPU.
"""
import torch


def resolve_device(device: str = "auto") -> torch.device:
    """Resolve a torch device.

    :param device: an explicit device string (e.g. ``"cpu"``, ``"cuda"``,
        ``"mps"``) or ``"auto"`` to pick the best available accelerator.
    :return: a :class:`torch.device` (CUDA, then MPS, then CPU by default).
    """
    if device and device != "auto":
        return torch.device(device)

    if torch.cuda.is_available():
        return torch.device("cuda")

    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def resolve_sparse_device(device: torch.device) -> torch.device:
    """Pick the device to build a sparse adjacency on.

    The Apple Metal (MPS) backend does not implement sparse matrix
    multiplication (``torch.sparse.mm`` / ``aten::addmm`` on the
    ``SparseMPS`` backend raises ``NotImplementedError``), whereas the CPU and
    CUDA backends do. When the model runs on MPS the sparse adjacency is kept on
    the CPU and the dense embedding is moved across for the matmul; otherwise the
    sparse adjacency shares the model device.
    """
    if device is not None and device.type == "mps":
        return torch.device("cpu")
    return device
