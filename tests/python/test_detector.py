from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from gpd.core import Cloud, Grasp, GraspDetector


def test_detector_constructs_from_config_path() -> None:
    config_path = Path(__file__).resolve().parents[2] / "cfg" / "eigen_params.cfg"

    detector = GraspDetector(config_path)

    assert detector is not None


def test_detector_config_path_resolves_relative_resources() -> None:
    config_path = Path(__file__).resolve().parents[2] / "cfg" / "eigen_params.cfg"

    detector = GraspDetector(config_path)
    cloud = _small_cloud()
    grasps = detector.detect_grasps(cloud)

    assert detector is not None
    assert len(grasps) > 0


def test_detector_constructs_from_eigen_preset() -> None:
    detector = GraspDetector.from_preset("eigen")

    assert detector is not None


def test_detector_rejects_unsupported_preset() -> None:
    with pytest.raises(ValueError, match="Unsupported GPD preset"):
        GraspDetector.from_preset("openvino")


def test_detector_detect_grasps_returns_list_for_numpy_cloud() -> None:
    detector = GraspDetector.from_preset("eigen")
    cloud = _small_cloud()

    grasps = detector.detect_grasps(cloud)

    assert isinstance(grasps, list)
    assert len(grasps) > 0


def test_grasp_exposes_core_fields() -> None:
    grasp = Grasp()

    assert grasp.position.shape == (3,)
    assert grasp.orientation.shape == (3, 3)
    assert grasp.approach.shape == (3,)
    assert isinstance(grasp.width, float)
    assert isinstance(grasp.score, float)
    assert isinstance(grasp.full_antipodal, bool)
    assert isinstance(grasp.half_antipodal, bool)


def _small_cloud() -> Cloud:
    return Cloud(
        np.array(
            [
                [0.0, 0.0, 0.0],
                [0.01, 0.0, 0.0],
                [0.0, 0.01, 0.0],
                [0.01, 0.01, 0.0],
            ],
            dtype=np.float64,
        )
    )
