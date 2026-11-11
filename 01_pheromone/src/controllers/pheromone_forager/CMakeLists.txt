add_library(pheromone_forager SHARED
  pheromone_forager.h
  pheromone_forager.cpp
  pheromone_forager_states.cpp
  pheromone_forager_params.cpp
  pheromone_forager_detractor.cpp
  pheromone_forager_defense.cpp)
target_link_libraries(pheromone_forager
  argos3core_simulator
  argos3plugin_simulator_footbot
  argos3plugin_simulator_genericrobot)
