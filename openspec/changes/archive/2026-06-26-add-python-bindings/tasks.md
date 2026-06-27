## 1. Packaging Foundation

- [x] 1.1 Add root `pyproject.toml` using `scikit_build_core.build` with `packaging/python` as the CMake source directory.
- [x] 1.2 Add Python package metadata for distribution name `gpd`, supported Python versions, dependencies, and package data.
- [x] 1.3 Create the `packaging/python` directory layout for CMake sources, nanobind sources, and `gpd/core` Python shims.
- [x] 1.4 Configure the Python CMake entrypoint to find Python, nanobind, NumPy, Eigen/cmeel dependencies, and the existing GPD native targets.

## 2. Core Binding API

- [x] 2.1 Implement the `_core` nanobind extension target under `packaging/python`.
- [x] 2.2 Bind `gpd.core.Cloud` construction from NumPy-compatible `(N, 3)` point arrays.
- [x] 2.3 Add optional `Cloud` handling for `view_points`, `normals`, and `sample_indices` with shape/type validation.
- [x] 2.4 Bind `gpd.core.GraspDetector` construction from config file paths.
- [x] 2.5 Add `GraspDetector.from_preset("eigen")` using packaged Eigen config files.
- [x] 2.6 Ensure unsupported presets raise clear Python exceptions and are not advertised as supported.

## 3. Result Mapping

- [x] 3.1 Implement a value-based Python-facing `gpd.core.Grasp` result type.
- [x] 3.2 Convert C++ `candidate::Hand` results into `Grasp` values with position, orientation, approach, width, score, full-antipodal status, and half-antipodal status.
- [x] 3.3 Implement `GraspDetector.detect_grasps(cloud)` returning `list[Grasp]` without exposing raw C++ ownership.

## 4. Python Package Surface

- [x] 4.1 Add `gpd/core` Python shim files that re-export the v1 API from the compiled extension.
- [x] 4.2 Preserve the PEP 420 namespace layout by not adding a required top-level `gpd/__init__.py`.
- [x] 4.3 Include supported Eigen config/package data needed by `from_preset("eigen")`.
- [x] 4.4 Add minimal package documentation or README notes for install, import, config, and v1 backend limitations.

## 5. Tests and Validation

- [x] 5.1 Add Python tests for importing `gpd.core` and the core API symbols.
- [x] 5.2 Add Python tests for valid and invalid `Cloud` array construction.
- [x] 5.3 Add Python tests for config-path construction and `from_preset("eigen")` behavior.
- [x] 5.4 Add Python tests that unsupported presets raise clear exceptions.
- [x] 5.5 Add result-mapping tests for `Grasp` field availability and ownership-safe return behavior.

## 6. Build CI

- [x] 6.1 Add build-only GitHub Actions workflow for Linux Python package builds.
- [x] 6.2 Configure CI to build the sdist or wheel for the selected Linux Python matrix.
- [x] 6.3 Configure CI smoke tests for `import gpd.core` and importing `Cloud`, `GraspDetector`, and `Grasp`.
- [x] 6.4 Ensure CI does not publish to PyPI or configure trusted publishing.

## 7. Regression Checks

- [x] 7.1 Verify the existing C++ build still configures and builds after adding Python packaging.
- [x] 7.2 Verify the Python package builds locally with the scikit-build-core entrypoint.
- [x] 7.3 Run OpenSpec validation for `add-python-bindings` and fix any artifact issues.
