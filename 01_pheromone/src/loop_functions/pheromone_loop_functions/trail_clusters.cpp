#include "trail_clusters.h"
#include <algorithm>
#include <cmath>
#include <map>
#include <numeric>

namespace pheromone
{
    namespace
    {
        const int UNVISITED = -2;
        const int NOISE = -1;

        std::vector<size_t> Neighbours(const std::vector<STrail> &vec_ends, size_t un_point, double f_eps)
        {
            std::vector<size_t> vecOut;
            for (size_t j = 0; j < vec_ends.size(); ++j)
                if (std::hypot(vec_ends[un_point].x - vec_ends[j].x, vec_ends[un_point].y - vec_ends[j].y) <= f_eps)
                    vecOut.push_back(j);
            return vecOut;
        }

        int Find(std::vector<int> &vec_parent, int n_node)
        {
            while (vec_parent[n_node] != n_node)
            {
                vec_parent[n_node] = vec_parent[vec_parent[n_node]];
                n_node = vec_parent[n_node];
            }
            return n_node;
        }
    }

    std::vector<int> DbscanLabels(const std::vector<STrail> &vec_ends, double f_eps, int n_min_pts)
    {
        std::vector<int> vecLabel(vec_ends.size(), UNVISITED);
        int nCluster = 0;
        for (size_t i = 0; i < vec_ends.size(); ++i)
        {
            if (vecLabel[i] != UNVISITED)
                continue;
            std::vector<size_t> vecSeeds = Neighbours(vec_ends, i, f_eps);
            if (static_cast<int>(vecSeeds.size()) < n_min_pts)
            {
                vecLabel[i] = NOISE;
                continue;
            }
            vecLabel[i] = nCluster;
            for (size_t k = 0; k < vecSeeds.size(); ++k)
            {
                const size_t j = vecSeeds[k];
                if (vecLabel[j] == NOISE)
                    vecLabel[j] = nCluster; /* a border point */
                if (vecLabel[j] != UNVISITED)
                    continue;
                vecLabel[j] = nCluster;
                const std::vector<size_t> vecMore = Neighbours(vec_ends, j, f_eps);
                if (static_cast<int>(vecMore.size()) >= n_min_pts)
                    vecSeeds.insert(vecSeeds.end(), vecMore.begin(), vecMore.end());
            }
            ++nCluster;
        }
        return vecLabel;
    }

    SGroups GroupTrails(const std::vector<STrail> &vec_ends, double f_eps, int n_min_pts)
    {
        SGroups sGroups;
        sGroups.clusterOfEnd = DbscanLabels(vec_ends, f_eps, n_min_pts);
        int nClusters = 0;
        for (int nLabel : sGroups.clusterOfEnd)
            nClusters = std::max(nClusters, nLabel + 1);
        for (int &nLabel : sGroups.clusterOfEnd)
            if (nLabel == NOISE)
                nLabel = nClusters++; /* a noise end becomes a cluster of one (section 3.3 step 3) */

        /* Union-find over clusters: two clusters with one creator are one node set. */
        std::vector<int> vecParent(nClusters);
        std::iota(vecParent.begin(), vecParent.end(), 0);
        std::map<int, int> mapCreatorCluster; /* creator -> first cluster seen */
        for (size_t i = 0; i < vec_ends.size(); ++i)
        {
            auto cIt = mapCreatorCluster.find(vec_ends[i].creator);
            if (cIt == mapCreatorCluster.end())
                mapCreatorCluster[vec_ends[i].creator] = sGroups.clusterOfEnd[i];
            else
                vecParent[Find(vecParent, sGroups.clusterOfEnd[i])] = Find(vecParent, cIt->second);
        }
        std::map<int, int> mapRootGroup; /* root cluster -> group index, in first-seen order */
        sGroups.groupOfEnd.resize(vec_ends.size());
        for (size_t i = 0; i < vec_ends.size(); ++i)
        {
            const int nRoot = Find(vecParent, sGroups.clusterOfEnd[i]);
            auto cIt = mapRootGroup.find(nRoot);
            if (cIt == mapRootGroup.end())
            {
                cIt = mapRootGroup.emplace(nRoot, static_cast<int>(sGroups.creators.size())).first;
                sGroups.creators.emplace_back();
            }
            sGroups.groupOfEnd[i] = cIt->second;
            sGroups.creators[cIt->second].push_back(vec_ends[i].creator);
        }
        for (std::vector<int> &vecCreators : sGroups.creators)
        {
            std::sort(vecCreators.begin(), vecCreators.end());
            vecCreators.erase(std::unique(vecCreators.begin(), vecCreators.end()), vecCreators.end());
        }
        return sGroups;
    }
}
