from __future__ import annotations


def test_core_import_exports_api() -> None:
    import gpd.core as core

    assert core.__version__
    assert core.Cloud is not None
    assert core.Grasp is not None
    assert core.GraspDetector is not None
    assert core.detect_grasps is not None
