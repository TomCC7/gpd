## Context

GPD currently exposes its functionality through C++ headers, a shared native library, and command-line executables. The repository also contains an orphaned `src/detect_grasps_python.cpp` C ABI adapter, but it is not wired into the CMake build and does not provide a modern Python package. The accepted v1 direction is to follow the roboplan-style packaging pattern with a dedicated Python build entrypoint while preserving the existing native build as the implementation source of truth.

The binding must use the domain term `Grasp` for Python-facing results. The C++ type `candidate::Hand` remains an implementation detail.

## Goals / Non-Goals

**Goals:**
- Provide a PyPI-buildable Python distribution named `gpd` with an importable `gpd.core` namespace submodule.
- Bind the minimal useful API: `Cloud`, `GraspDetector`, and value-based `Grasp` results.
- Accept NumPy arrays for point cloud data, normals, view points, and sample indices.
- Support detector construction from config file paths and `GraspDetector.from_preset("eigen")`.
- Build the first wheel with Eigen-only detection support.
- Add build-only CI that validates packaging and importability without publishing.

**Non-Goals:**
- No Caffe or OpenVINO Python presets in v1.
- No publishing workflow, trusted PyPI publishing setup, or release automation in v1.
- No Windows wheels in v1.
- No macOS wheels until native dependency discovery is proven stable.
- No dependency on Open3D, ROS, or Python PCL packages for core input handling.
- No direct exposure of raw `std::unique_ptr<candidate::Hand>` lifetimes to Python callers.

## Decisions

1. **Use a dedicated `packaging/python` scikit-build-core entrypoint.**
   - Decision: add root Python packaging metadata that points scikit-build-core at `packaging/python`.
   - Rationale: keeps root CMake focused on the existing C++ library and tools while isolating Python package concerns.
   - Alternative considered: make root `CMakeLists.txt` the Python packaging root. Rejected because it would mix package-building concerns into the native build and make the first binding change riskier.

2. **Use nanobind for the compiled extension.**
   - Decision: build a `_core` extension with nanobind and expose stable Python wrappers from `gpd.core`.
   - Rationale: nanobind matches the roboplan pattern and gives direct C++ bindings without maintaining a separate C ABI.
   - Alternative considered: reuse `src/detect_grasps_python.cpp`. Rejected because it is orphaned from the build and appears stale against the current C++ headers.

3. **Expose a PEP 420 namespace package with no top-level `gpd/__init__.py`.**
   - Decision: install the submodule under `gpd/core` and avoid a top-level namespace initializer.
   - Rationale: follows the roboplan namespace convention and leaves room for future independently packaged submodules without changing the import model.
   - Alternative considered: monolithic top-level `gpd/__init__.py`. Rejected because it is less flexible and diverges from the packaging model being followed.

4. **Return value-based `Grasp` objects.**
   - Decision: convert C++ `candidate::Hand` results into Python-facing `Grasp` values containing position, orientation, approach, width, score, and antipodal flags.
   - Rationale: avoids ownership and lifetime hazards from exposing a vector of `std::unique_ptr<candidate::Hand>` directly.
   - Alternative considered: bind `candidate::Hand` directly. Rejected for v1 because Python callers need stable result data more than mutable access to C++ internals.

5. **Keep v1 backend scope Eigen-only.**
   - Decision: ship only the Eigen preset in Python packaging until optional classifier runtimes are deliberately packaged and tested.
   - Rationale: avoids advertising Caffe/OpenVINO support that the wheel cannot reliably provide.
   - Alternative considered: expose all existing config presets. Rejected because backend availability depends on compile-time features and external runtimes.

6. **Add build-only CI, not publish CI.**
   - Decision: CI builds sdist/wheels and runs import smoke tests, but does not upload artifacts to PyPI.
   - Rationale: validates the packaging path without creating release-management obligations before the binding is proven.
   - Alternative considered: semver tag publishing workflow with trusted publishing. Rejected for v1 per accepted scope.

## Risks / Trade-offs

- Native dependency packaging may fail in CI or wheel builds → Start Linux-first and keep the first backend Eigen-only.
- Eigen-only support may disappoint users with existing Caffe/OpenVINO configs → Expose only supported presets and keep path-based config for advanced local builds.
- PEP 420 namespace packaging can surprise maintainers expecting a top-level `__init__.py` → Document the import model and test `import gpd.core` in CI.
- Value-based `Grasp` results may omit fields some users need → Keep the v1 schema focused and extend it with additional read-only fields as requirements emerge.
- Separate Python CMake entrypoint may duplicate some build logic → Keep it thin and delegate native library construction/linking to existing CMake targets where possible.

## Migration Plan

1. Add Python packaging metadata and the `packaging/python` build entrypoint.
2. Add nanobind bindings and Python shims for `gpd.core`.
3. Add package data for the supported Eigen preset/config files.
4. Add build-only CI for Linux Python versions and import smoke tests.
5. Validate that existing C++ build and command-line workflows still work.

Rollback is straightforward before publication: remove the Python packaging files, binding sources, and CI workflow. Existing C++ behavior should remain unaffected.

## Open Questions

- Which exact Python versions should the first CI matrix include if native dependency build time becomes too high?
- Should `Grasp` expose additional fields from `candidate::Hand` in v1, or defer them until a user need appears?
