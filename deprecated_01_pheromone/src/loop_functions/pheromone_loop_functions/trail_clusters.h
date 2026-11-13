#ifndef TRAIL_CLUSTERS_H
#define TRAIL_CLUSTERS_H

#include "trail_store.h"
#include <vector>

/*
 * Density clustering of trail ends and the creator-ID graph (DESIGN_M6 section 3.3).
 * Plain C++, no library (D-045). Pure and deterministic: the result depends only on the
 * order of the input.
 */
namespace pheromone
{
    /* Density-based spatial clustering of applications with noise (DBSCAN).
       A point is core when at least n_min_pts points (itself included) lie within f_eps.
       Returns one label per point: 0, 1, ... or -1 for noise. */
    std::vector<int> DbscanLabels(const std::vector<STrail> &vec_ends, double f_eps, int n_min_pts);

    struct SGroups
    {
        std::vector<int> clusterOfEnd;             /* per input end. A noise end is a cluster of one */
        std::vector<int> groupOfEnd;               /* per input end */
        std::vector<std::vector<int>> creators;    /* per group: sorted creator indexes, no repeat */
    };

    /* Clusters are the nodes, an edge joins two clusters that share a creator, groups are the
       connected components. */
    SGroups GroupTrails(const std::vector<STrail> &vec_ends, double f_eps, int n_min_pts);
}

#endif
