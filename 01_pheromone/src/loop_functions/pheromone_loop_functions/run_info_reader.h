#ifndef RUN_INFO_READER_H
#define RUN_INFO_READER_H

#include "run_logger.h"
#include <argos3/core/utility/configuration/argos_configuration.h>

/*
 * Fills SRunInfo from the .argos file: the <logger> stamps written by
 * tools/make_sweep.py and every other value for manifest params.
 * Returns false when there is no <logger> node (the Qt demo): no logging then.
 * Layout, decoys used and code_version are set by the caller.
 */
bool ReadRunInfo(argos::TConfigurationNode &t_loop_functions, pheromone::SRunInfo &s_info);

#endif
