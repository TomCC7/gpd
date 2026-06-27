from __future__ import annotations

import numpy as np
import pytest

from gpd.core import Cloud


def test_cloud_accepts_points() -> None:
    points = np.array([[0.0, 0.0, 0.0], [0.1, 0.2, 0.3]], dtype=np.float64)

    cloud = Cloud(points)

    assert cloud is not None


def test_cloud_accepts_optional_metadata() -> None:
    points = np.array([[0.0, 0.0, 0.0], [0.1, 0.2, 0.3]], dtype=np.float64)
    view_points = np.array([[0.0, 0.0, 0.0]], dtype=np.float64)
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64)
    sample_indices = np.array([0, 1], dtype=np.int32)

    cloud = Cloud(points, view_points=view_points, normals=normals, sample_indices=sample_indices)

    assert cloud is not None


@pytest.mark.parametrize(
    "points",
    [
        np.array([0.0, 0.0, 0.0], dtype=np.float64),
        np.array([[0.0, 0.0]], dtype=np.float64),
    ],
)
def test_cloud_rejects_invalid_point_shape(points: np.ndarray) -> None:
    with pytest.raises((TypeError, ValueError), match="shape|incompatible"):
        Cloud(points)


@pytest.mark.parametrize(
    "sample_indices",
    [
        np.array([-1], dtype=np.int32),
        np.array([2], dtype=np.int32),
        np.array([[0]], dtype=np.int32),
    ],
)
def test_cloud_rejects_invalid_sample_indices(sample_indices: np.ndarray) -> None:
    points = np.array([[0.0, 0.0, 0.0], [0.1, 0.2, 0.3]], dtype=np.float64)

    with pytest.raises(ValueError, match="sample_indices"):
        Cloud(points, sample_indices=sample_indices)
