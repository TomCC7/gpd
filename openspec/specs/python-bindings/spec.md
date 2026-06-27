## Purpose

Define the Python binding and package behavior for GPD's `gpd.core` API.

## Requirements

### Requirement: Python package import surface
The system SHALL provide a Python distribution named `gpd` with an importable `gpd.core` submodule using a PEP 420 namespace layout with no required top-level `gpd/__init__.py` file.

#### Scenario: Import core module
- **WHEN** a user installs the Python package and imports `gpd.core`
- **THEN** the import succeeds and exposes the v1 core API symbols

### Requirement: NumPy-first cloud construction
The system SHALL allow Python users to construct `gpd.core.Cloud` from NumPy-compatible point arrays, with optional view points, normals, and sample indices.

#### Scenario: Construct cloud from points
- **WHEN** a user creates `Cloud(points)` with a valid `(N, 3)` numeric point array
- **THEN** the system creates a cloud object usable by `GraspDetector`

#### Scenario: Construct cloud with optional metadata
- **WHEN** a user creates `Cloud(points, view_points=view_points, normals=normals, sample_indices=sample_indices)` with compatible array shapes
- **THEN** the system preserves the supplied metadata for detection

#### Scenario: Reject invalid cloud shape
- **WHEN** a user creates `Cloud(points)` with an invalid point array shape
- **THEN** the system raises a Python exception explaining the expected shape

### Requirement: Detector configuration
The system SHALL allow Python users to construct `gpd.core.GraspDetector` from a config file path and from the supported preset `GraspDetector.from_preset("eigen")`.

#### Scenario: Construct detector from config path
- **WHEN** a user creates `GraspDetector(config_path)` with a valid config path
- **THEN** the system creates a detector using that configuration

#### Scenario: Construct detector from Eigen preset
- **WHEN** a user calls `GraspDetector.from_preset("eigen")`
- **THEN** the system creates a detector using the packaged Eigen configuration

#### Scenario: Reject unsupported preset
- **WHEN** a user calls `GraspDetector.from_preset()` with any preset other than `"eigen"`
- **THEN** the system raises a Python exception that the preset is unsupported by the installed package

### Requirement: Grasp detection result values
The system SHALL return detected grasps as Python-facing `gpd.core.Grasp` values rather than exposing raw C++ result ownership.

#### Scenario: Detect grasps from a cloud
- **WHEN** a user calls `detector.detect_grasps(cloud)` with a valid `Cloud`
- **THEN** the system returns a Python list of `Grasp` values

#### Scenario: Grasp exposes core fields
- **WHEN** a user receives a `Grasp` value
- **THEN** the value exposes position, orientation, approach, width, score, full-antipodal status, and half-antipodal status

### Requirement: Eigen-only packaged backend
The system SHALL expose only backend presets supported by the v1 Python wheel build.

#### Scenario: Optional classifiers are unavailable in v1 wheel
- **WHEN** a user requests Caffe or OpenVINO through a Python preset
- **THEN** the system does not advertise those presets and reports them as unsupported

### Requirement: Build-only Python CI
The system SHALL include CI that verifies the Python package builds and imports without publishing artifacts to PyPI.

#### Scenario: CI builds package
- **WHEN** CI runs for a push or pull request
- **THEN** it builds the Python sdist or wheel successfully for the configured Linux Python matrix

#### Scenario: CI smoke-tests imports
- **WHEN** CI finishes building the Python package
- **THEN** it verifies `import gpd.core` and imports the core API symbols

#### Scenario: CI does not publish
- **WHEN** CI runs for the v1 binding change
- **THEN** it does not upload distributions to PyPI or configure trusted publishing
