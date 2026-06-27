#include <array>
#include <cstdint>
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include <Eigen/Dense>
#include <gpd/candidate/hand.h>
#include <gpd/grasp_detector.h>
#include <gpd/util/cloud.h>
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>

namespace nb = nanobind;

namespace {

using DoubleMatrix = nb::ndarray<const double, nb::c_contig, nb::ndim<2>>;
using IntVector = nb::ndarray<const int, nb::c_contig, nb::ndim<1>>;

struct GraspValue {
  std::array<double, 3> position{};
  std::array<double, 9> orientation{};
  std::array<double, 3> approach{};
  double width{0.0};
  double score{0.0};
  bool full_antipodal{false};
  bool half_antipodal{false};
};

void require_matrix_shape(const DoubleMatrix &array, const char *name,
                          std::size_t columns) {
  if (array.shape(1) != columns) {
    throw std::invalid_argument(std::string(name) + " must have shape (N, " +
                                std::to_string(columns) + ")");
  }
}

Eigen::Matrix3Xd rows_to_eigen3x(const DoubleMatrix &array,
                                 const char *name) {
  require_matrix_shape(array, name, 3);
  Eigen::Matrix3Xd matrix(3, array.shape(0));
  const double *data = array.data();
  for (std::size_t row = 0; row < array.shape(0); ++row) {
    matrix(0, row) = data[row * 3];
    matrix(1, row) = data[row * 3 + 1];
    matrix(2, row) = data[row * 3 + 2];
  }
  return matrix;
}

std::vector<int> to_indices(const IntVector &array) {
  std::vector<int> indices(array.shape(0));
  const int *data = array.data();
  for (std::size_t i = 0; i < array.shape(0); ++i) {
    indices[i] = data[i];
  }
  return indices;
}

gpd::util::Cloud make_cloud(const DoubleMatrix &points, nb::object view_points,
                            nb::object normals, nb::object sample_indices) {
  require_matrix_shape(points, "points", 3);
  auto cloud(new gpd::util::PointCloudRGB);
  cloud->points.resize(points.shape(0));
  cloud->width = static_cast<std::uint32_t>(points.shape(0));
  cloud->height = 1;
  cloud->is_dense = false;

  const double *data = points.data();
  for (std::size_t row = 0; row < points.shape(0); ++row) {
    auto &point = cloud->points[row];
    point.x = static_cast<float>(data[row * 3]);
    point.y = static_cast<float>(data[row * 3 + 1]);
    point.z = static_cast<float>(data[row * 3 + 2]);
    point.r = 255;
    point.g = 255;
    point.b = 255;
    point.a = 255;
  }

  Eigen::Matrix3Xd view_points_matrix(3, 1);
  view_points_matrix << 0.0, 0.0, 0.0;
  if (!view_points.is_none()) {
    view_points_matrix = rows_to_eigen3x(nb::cast<DoubleMatrix>(view_points),
                                         "view_points");
  }

  Eigen::MatrixXi camera_source = Eigen::MatrixXi::Ones(
      static_cast<int>(view_points_matrix.cols()), static_cast<int>(points.shape(0)));
  gpd::util::Cloud result(gpd::util::PointCloudRGB::Ptr(cloud), camera_source,
                          view_points_matrix);

  if (!normals.is_none()) {
    const DoubleMatrix normal_array = nb::cast<DoubleMatrix>(normals);
    if (normal_array.shape(0) != points.shape(0)) {
      throw std::invalid_argument("normals must have the same row count as points");
    }
    result.setNormals(rows_to_eigen3x(normal_array, "normals"));
  }

  if (!sample_indices.is_none()) {
    result.setSampleIndices(to_indices(nb::cast<IntVector>(sample_indices)));
  }

  return result;
}

GraspValue to_grasp_value(const gpd::candidate::Hand &hand) {
  GraspValue grasp;
  const Eigen::Vector3d &position = hand.getPosition();
  const Eigen::Matrix3d &orientation = hand.getOrientation();
  const Eigen::Vector3d approach = hand.getApproach();

  for (std::size_t i = 0; i < 3; ++i) {
    grasp.position[i] = position(static_cast<int>(i));
    grasp.approach[i] = approach(static_cast<int>(i));
  }
  for (std::size_t row = 0; row < 3; ++row) {
    for (std::size_t col = 0; col < 3; ++col) {
      grasp.orientation[row * 3 + col] =
          orientation(static_cast<int>(row), static_cast<int>(col));
    }
  }

  grasp.width = hand.getGraspWidth();
  grasp.score = hand.getScore();
  grasp.full_antipodal = hand.isFullAntipodal();
  grasp.half_antipodal = hand.isHalfAntipodal();
  return grasp;
}

std::vector<GraspValue> detect_grasps(gpd::GraspDetector &detector,
                                       const gpd::util::Cloud &cloud) {
  gpd::util::Cloud preprocessed_cloud = cloud;
  detector.preprocessPointCloud(preprocessed_cloud);
  std::vector<std::unique_ptr<gpd::candidate::Hand>> hands =
      detector.detectGrasps(preprocessed_cloud);
  std::vector<GraspValue> grasps;
  grasps.reserve(hands.size());
  for (const auto &hand : hands) {
    if (hand) {
      grasps.push_back(to_grasp_value(*hand));
    }
  }
  return grasps;
}

template <std::size_t Size>
nb::ndarray<nb::numpy, double, nb::ndim<1>> array1d(
    const std::array<double, Size> &values) {
  double *data = new double[Size];
  for (std::size_t i = 0; i < Size; ++i) {
    data[i] = values[i];
  }
  nb::capsule owner(data, [](void *ptr) noexcept { delete[] static_cast<double *>(ptr); });
  return nb::ndarray<nb::numpy, double, nb::ndim<1>>(data, {Size}, owner);
}

nb::ndarray<nb::numpy, double, nb::ndim<2>> orientation_array(
    const GraspValue &grasp) {
  double *data = new double[9];
  for (std::size_t i = 0; i < 9; ++i) {
    data[i] = grasp.orientation[i];
  }
  nb::capsule owner(data, [](void *ptr) noexcept { delete[] static_cast<double *>(ptr); });
  return nb::ndarray<nb::numpy, double, nb::ndim<2>>(data, {3, 3}, owner);
}

}  // namespace

NB_MODULE(_core_ext, module) {
  module.doc() = "Core Python bindings for GPD";
  module.attr("__version__") = GPD_PYTHON_VERSION;

  nb::class_<gpd::util::Cloud>(module, "Cloud")
      .def(nb::new_([](const DoubleMatrix &points, nb::object view_points,
                       nb::object normals, nb::object sample_indices) {
             return make_cloud(points, view_points, normals, sample_indices);
           }),
           nb::arg("points"), nb::arg("view_points") = nb::none(),
           nb::arg("normals") = nb::none(),
           nb::arg("sample_indices") = nb::none());

  nb::class_<GraspValue>(module, "Grasp")
      .def(nb::init<>())
      .def_prop_ro("position", [](const GraspValue &grasp) { return array1d(grasp.position); },
                   nb::rv_policy::move)
      .def_prop_ro("orientation", orientation_array, nb::rv_policy::move)
      .def_prop_ro("approach", [](const GraspValue &grasp) { return array1d(grasp.approach); },
                   nb::rv_policy::move)
      .def_ro("width", &GraspValue::width)
      .def_ro("score", &GraspValue::score)
      .def_ro("full_antipodal", &GraspValue::full_antipodal)
      .def_ro("half_antipodal", &GraspValue::half_antipodal);

  nb::class_<gpd::GraspDetector>(module, "GraspDetector")
      .def(nb::init<const std::string &>(), nb::arg("config_path"))
      .def("detect_grasps", &detect_grasps, nb::arg("cloud"));
}
