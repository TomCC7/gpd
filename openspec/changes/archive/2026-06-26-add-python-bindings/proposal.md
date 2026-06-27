## Why

GPD currently builds as a C++ library and command-line tool, but it does not provide a maintained Python package or PyPI wheel path. A clean Python binding will make grasp detection usable from Python workflows while preserving the existing C++ API as the implementation source of truth.

## What Changes

- Add a Python package distribution named `gpd` exposing a `gpd.core` namespace submodule.
- Add nanobind-based bindings for the minimal v1 API: `Cloud`, `GraspDetector`, and value-based `Grasp` results.
- Add NumPy-first point cloud input for `Cloud` construction.
- Add path-based detector configuration plus `GraspDetector.from_preset("eigen")` for the supported v1 preset.
- Add a scikit-build-core packaging entrypoint under `packaging/python` while keeping the root C++ build focused on the existing native library and tools.
- Add build-only CI that verifies Python wheel/sdist construction and import smoke tests without publishing to PyPI.
- Defer Caffe/OpenVINO Python presets, publishing workflows, macOS wheels, Windows wheels, and non-NumPy Python point-cloud dependencies.

## Capabilities

### New Capabilities
- `python-bindings`: Python package, import surface, binding API, packaging, and build verification for the v1 GPD Python interface.

### Modified Capabilities

## Impact

- Adds Python packaging metadata and a dedicated scikit-build-core CMake entrypoint.
- Adds nanobind and Python/NumPy build/runtime integration.
- Adds Python-facing API files under the `gpd.core` namespace.
- Adds build-only CI for Python package validation.
- Does not change the existing C++ public API or command-line behavior.
