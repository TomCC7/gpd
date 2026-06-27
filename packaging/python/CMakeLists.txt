cmake_minimum_required(VERSION 3.18...3.27)
project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Python 3.10 REQUIRED COMPONENTS Interpreter Development.Module NumPy)

execute_process(
  COMMAND "${Python_EXECUTABLE}" -c "import pathlib, site; prefixes=[pathlib.Path(p) / 'cmeel.prefix' for p in site.getsitepackages()]; print(next((str(p) for p in prefixes if p.exists()), ''))"
  OUTPUT_VARIABLE CMEEL_PREFIX
  OUTPUT_STRIP_TRAILING_WHITESPACE
  ERROR_QUIET
)
if(CMEEL_PREFIX)
  list(PREPEND CMAKE_PREFIX_PATH "${CMEEL_PREFIX}")
endif()

if(DEFINED ENV{CONDA_PREFIX})
  list(PREPEND CMAKE_PREFIX_PATH "$ENV{CONDA_PREFIX}")
endif()

list(PREPEND CMAKE_PREFIX_PATH "${Python_SITEARCH}" "${Python_SITELIB}")

find_package(nanobind CONFIG REQUIRED)
find_package(X11 QUIET)
find_library(X11_LIBRARY NAMES X11 PATHS "$ENV{CONDA_PREFIX}/lib")
find_package(Eigen3 CONFIG QUIET)
find_path(EIGEN3_INCLUDE_DIR Eigen/Dense
  PATHS
    "${CMEEL_PREFIX}/include/eigen3"
    "$ENV{CONDA_PREFIX}/include/eigen3"
    /usr/include/eigen3
)
if(NOT EIGEN3_INCLUDE_DIR)
  message(FATAL_ERROR "Could not find Eigen headers")
endif()
if(NOT TARGET Eigen3::Eigen)
  add_library(Eigen3::Eigen INTERFACE IMPORTED)
  target_include_directories(Eigen3::Eigen INTERFACE "${EIGEN3_INCLUDE_DIR}")
endif()

get_filename_component(GPD_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)

add_subdirectory("${GPD_SOURCE_DIR}" "${CMAKE_BINARY_DIR}/gpd-native" EXCLUDE_FROM_ALL)

nanobind_add_module(
  _core_ext
  STABLE_ABI
  NB_STATIC
  src/core_ext.cpp
)

target_include_directories(_core_ext PRIVATE
  "${GPD_SOURCE_DIR}/include"
  ${Python_NumPy_INCLUDE_DIRS}
)

target_link_libraries(_core_ext PRIVATE
  gpd_grasp_detector
  gpd_cloud
  Eigen3::Eigen
)

if(X11_FOUND)
  target_link_libraries(_core_ext PRIVATE -Wl,--no-as-needed ${X11_LIBRARIES} -Wl,--as-needed)
elseif(X11_LIBRARY)
  target_link_libraries(_core_ext PRIVATE -Wl,--no-as-needed ${X11_LIBRARY} -Wl,--as-needed)
endif()

set_target_properties(_core_ext PROPERTIES
  INSTALL_RPATH "$ORIGIN/../../lib"
)

target_compile_definitions(_core_ext PRIVATE GPD_PYTHON_VERSION="${SKBUILD_PROJECT_VERSION}")

install(TARGETS _core_ext LIBRARY DESTINATION gpd/core)
install(TARGETS gpd_grasp_detector LIBRARY DESTINATION lib)
install(DIRECTORY python/gpd/core/ DESTINATION gpd/core FILES_MATCHING PATTERN "*.py")
install(DIRECTORY "${GPD_SOURCE_DIR}/cfg/" DESTINATION gpd/core/cfg FILES_MATCHING PATTERN "*.cfg")
install(DIRECTORY "${GPD_SOURCE_DIR}/models/lenet/" DESTINATION gpd/core/models/lenet)
