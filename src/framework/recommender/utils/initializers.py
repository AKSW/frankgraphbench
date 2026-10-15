"""Weight initializers matching the original TensorFlow ``VarianceScaling``.

The converted models used to initialize their embedding tables with
``tf.compat.v1.keras.initializers.VarianceScaling``. ``variance_scaling``
reproduces the same uniform / truncated-normal draws so the PyTorch
implementations stay numerically close to the original TensorFlow versions.
"""
import math

import torch
from torch import nn


def variance_scaling(shape, distribution="uniform", scale=1.0, device=None):
    """Draw a tensor mimicking ``tf.keras.initializers.VarianceScaling``.

    The fan-in/fan-out follow the TensorFlow convention: ``output_dim`` is the
    product of all but the last dimension and ``input_dim`` the product of all
    but the first. ``fan_avg = (fan_in + fan_out) / 2`` and ``variance =
    scale / fan_avg``.
    """
    output_dim = 1.0
    for dim in shape[:-1]:
        output_dim *= dim
    input_dim = 1.0
    for dim in shape[1:]:
        input_dim *= dim

    if len(shape) <= 1:
        # 0-D or 1-D parameters have no meaningful fan-in/out; fall back to 1.
        fan_avg = 1.0
    else:
        fan_avg = (input_dim + output_dim) / 2.0

    variance = scale / fan_avg

    tensor = torch.empty(shape, dtype=torch.float32)

    if distribution == "uniform":
        limit = math.sqrt(3.0 * variance)
        nn.init.uniform_(tensor, -limit, limit)
    else:  # "truncated_normal"
        std = math.sqrt(variance)
        nn.init.trunc_normal_(tensor, mean=0.0, std=std, a=-2.0 * std, b=2.0 * std)

    if device is not None:
        tensor = tensor.to(device)
    return tensor
