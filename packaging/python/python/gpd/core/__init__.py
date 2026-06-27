from __future__ import annotations

from importlib import resources
from pathlib import Path
import tempfile
from typing import Final

import numpy as np
import numpy.typing as npt

from ._core_ext import Grasp, __version__
from ._core_ext import Cloud as _Cloud
from ._core_ext import GraspDetector as _GraspDetector

_SUPPORTED_PRESETS: Final[frozenset[str]] = frozenset({"eigen"})


class Cloud(_Cloud):
    """Point-cloud input for grasp detection."""

    def __new__(
        cls,
        points: npt.ArrayLike,
        view_points: npt.ArrayLike | None = None,
        normals: npt.ArrayLike | None = None,
        sample_indices: npt.ArrayLike | None = None,
    ) -> "Cloud":
        points_array = _as_matrix(points, "points")
        view_points_array = None if view_points is None else _as_matrix(view_points, "view_points")
        normals_array = None if normals is None else _as_matrix(normals, "normals")
        if normals_array is not None and normals_array.shape[0] != points_array.shape[0]:
            raise ValueError("normals must have the same row count as points")
        sample_indices_array = (
            None if sample_indices is None else _as_sample_indices(sample_indices, points_array.shape[0])
        )
        return _Cloud.__new__(
            cls,
            points_array,
            view_points_array,
            normals_array,
            sample_indices_array,
        )


def _as_matrix(values: npt.ArrayLike, name: str) -> np.ndarray:
    array = np.ascontiguousarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"{name} must have shape (N, 3)")
    return array


def _as_sample_indices(values: npt.ArrayLike, point_count: int) -> np.ndarray:
    array = np.ascontiguousarray(values, dtype=np.int32)
    if array.ndim != 1:
        raise ValueError("sample_indices must have shape (N,)")
    if array.size > 0 and (np.any(array < 0) or np.any(array >= point_count)):
        raise ValueError("sample_indices must satisfy 0 <= index < len(points)")
    return array


def _write_config_copy(config: str) -> Path:
    copied_config = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".cfg", delete=False)
    with copied_config:
        copied_config.write(config)
    return Path(copied_config.name)


def _rewrite_config_paths(config: str, base_dir: Path) -> str:
    path_keys = frozenset({"hand_geometry_filename", "image_geometry_filename", "model_file", "weights_file"})
    rewritten_lines: list[str] = []
    for line in config.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            rewritten_lines.append(line)
            continue

        key, value = line.split("=", 1)
        key_name = key.strip()
        value_text = value.strip()
        if key_name not in path_keys or not value_text or Path(value_text).is_absolute():
            rewritten_lines.append(line)
            continue

        resolved_path = str(base_dir.joinpath(value_text).resolve())
        if value_text.endswith(("/", "\\")):
            resolved_path += "/"
        rewritten_lines.append(f"{key.rstrip()} = {resolved_path}")
    return "\n".join(rewritten_lines) + "\n"


def _disable_plotting(config: str) -> str:
    plot_keys = frozenset(
        {
            "plot_normals",
            "plot_samples",
            "plot_candidates",
            "plot_filtered_candidates",
            "plot_valid_grasps",
            "plot_clustered_grasps",
            "plot_selected_grasps",
        }
    )
    rewritten_lines: list[str] = []
    for line in config.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            rewritten_lines.append(line)
            continue

        key, _value = line.split("=", 1)
        if key.strip() in plot_keys:
            rewritten_lines.append(f"{key.rstrip()} = 0")
        else:
            rewritten_lines.append(line)
    return "\n".join(rewritten_lines) + "\n"


def _materialize_config(config_path: str | Path) -> Path:
    source_path = Path(config_path).expanduser()
    config = source_path.read_text(encoding="utf-8")
    return _write_config_copy(_disable_plotting(_rewrite_config_paths(config, source_path.parent)))


def _materialize_preset_config() -> Path:
    package_root = resources.files(__package__)
    config_path = package_root.joinpath("cfg", "eigen_params.cfg")
    cfg_dir = Path(str(package_root.joinpath("cfg")))
    models_dir = Path(str(package_root.joinpath("models")))

    config = config_path.read_text(encoding="utf-8")
    config = config.replace("../cfg/hand_geometry.cfg", str(cfg_dir / "hand_geometry.cfg"))
    config = config.replace(
        "../cfg/image_geometry_15channels.cfg",
        str(cfg_dir / "image_geometry_15channels.cfg"),
    )
    config = config.replace(
        "../models/lenet/15channels/params/",
        str(models_dir / "lenet" / "15channels" / "params") + "/",
    )

    return _write_config_copy(_disable_plotting(config))


class GraspDetector(_GraspDetector):
    """Detector configured from a GPD config file."""

    def __init__(self, config_path: str | Path) -> None:
        super().__init__(str(_materialize_config(config_path)))

    @classmethod
    def from_preset(cls, preset: str) -> "GraspDetector":
        if preset not in _SUPPORTED_PRESETS:
            supported = ", ".join(sorted(_SUPPORTED_PRESETS))
            raise ValueError(f"Unsupported GPD preset {preset!r}. Supported presets: {supported}")

        return cls(str(_materialize_preset_config()))


def detect_grasps(cloud: Cloud, config_path: str | Path | None = None) -> list[Grasp]:
    """Detect grasps with either a config path or the Eigen preset."""

    detector = GraspDetector.from_preset("eigen") if config_path is None else GraspDetector(str(config_path))
    return detector.detect_grasps(cloud)


__all__ = ["Cloud", "Grasp", "GraspDetector", "__version__", "detect_grasps"]
