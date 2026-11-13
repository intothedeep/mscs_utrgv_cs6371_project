link_directories(${CMAKE_BINARY_DIR}/controllers/pheromone_forager)
# pheromone_grid and food_field are pure C++ (no ARGoS include); they are
# compiled into the loop-function module, not a separate library.
set(pheromone_loop_functions_SOURCES
  pheromone_grid.cpp
  food_field.cpp
  owner_grid.cpp
  trail_store.cpp
  trail_clusters.cpp
  id_defense.cpp
  defense_log.cpp
  id_arm.cpp
  pheromone_loop_functions.cpp
  pheromone_loop_functions_id.cpp
  pheromone_loop_functions_log.cpp
  run_logger.cpp
  run_info_reader.cpp)

# The Qt user functions exist only when ARGoS was built with Qt-OpenGL.
if(ARGOS_QTOPENGL_FOUND)
  include_directories(${ARGOS_QTOPENGL_INCLUDE_DIRS})
  set(pheromone_loop_functions_SOURCES
    ${pheromone_loop_functions_SOURCES}
    pheromone_qt_user_functions.cpp)
endif(ARGOS_QTOPENGL_FOUND)

add_library(pheromone_loop_functions MODULE ${pheromone_loop_functions_SOURCES})
target_link_libraries(pheromone_loop_functions
  pheromone_forager
  argos3core_simulator
  argos3plugin_simulator_dynamics2d
  argos3plugin_simulator_entities
  argos3plugin_simulator_footbot
  argos3plugin_simulator_genericrobot
  argos3plugin_simulator_media)

if(ARGOS_QTOPENGL_FOUND)
  target_link_libraries(pheromone_loop_functions argos3plugin_simulator_qtopengl)
endif(ARGOS_QTOPENGL_FOUND)
