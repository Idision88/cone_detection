cmake_minimum_required(VERSION 2.8.3)
project(cone_detection)

find_package(catkin_simple 0.1.0 REQUIRED COMPONENTS
	roscpp
	rospy
	geometry_msgs
	nav_msgs
	sensor_msgs
 	pcl_conversions
  	pcl_ros
  	OpenCV  REQUIRED
  	eigen_catkin
	catkin_simple REQUIRED
)

catkin_simple(ALL_DEPS_REQUIRED)

cs_add_library(${PROJECT_NAME}
	  src/grid_mapper.cpp 
	  src/image_handler.cpp
    src/laser_detection.cpp
    src/tools.cpp
    src/car_model.cpp
    planning/pure_pursuit.cpp
    planning/tools.cpp
    planning/planner.cpp
)

cs_add_executable(cone_detector src/main.cpp)
target_link_libraries(cone_detector ${catkin_LIBRARIES} ${PROJECT_NAME})

cs_add_executable(path_planner planning/main.cpp)
target_link_libraries(path_planner ${catkin_LIBRARIES} ${PROJECT_NAME})

cs_add_executable(interface planning/interface.cpp)
target_link_libraries(interface ${catkin_LIBRARIES} ${PROJECT_NAME})

cs_install()
cs_export()




