#include "food_field.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace pheromone
{
    static double Distance(const SPoint &s_a, const SPoint &s_b)
    {
        return std::hypot(s_a.x - s_b.x, s_a.y - s_b.y);
    }

    void CFoodField::Draw(const TUniform &f_uniform)
    {
        static const int MAX_TRIES = 10000;
        m_vecSources.clear();
        m_vecDecoys.clear();
        for (int i = 0; i < NUM_SOURCES; ++i)
            m_vecSources.push_back({f_uniform(SOURCE_X_MIN, SOURCE_X_MAX),
                                    f_uniform(-SPOT_Y_LIMIT, SPOT_Y_LIMIT)});
        for (int i = 0; i < NUM_DECOYS; ++i)
        {
            bool bPlaced = false;
            for (int nTry = 0; nTry < MAX_TRIES && !bPlaced; ++nTry)
            {
                SPoint sCandidate{f_uniform(DECOY_X_MIN, SOURCE_X_MAX),
                                  f_uniform(-SPOT_Y_LIMIT, SPOT_Y_LIMIT)};
                double fBand = Distance(sCandidate, {NEST_EDGE_X, 0.0});
                bool bClear = fBand >= DECOY_BAND_MIN && fBand <= DECOY_BAND_MAX;
                for (const SPoint &sSource : m_vecSources)
                    bClear = bClear && Distance(sCandidate, sSource) >= MIN_DECOY_GAP_M;
                if (bClear)
                {
                    m_vecDecoys.push_back(sCandidate);
                    bPlaced = true;
                }
            }
            if (!bPlaced)
                throw std::runtime_error("food_field: no decoy spot meets the 1.5 m gap");
        }
    }

    std::vector<SPoint> CFoodField::ActiveDecoys(unsigned n_det) const
    {
        size_t unUsed = std::min<size_t>(n_det, m_vecDecoys.size());
        return std::vector<SPoint>(m_vecDecoys.begin(), m_vecDecoys.begin() + unUsed);
    }

    bool CFoodField::IsOnSource(double f_x, double f_y) const
    {
        for (const SPoint &sSource : m_vecSources)
            if (Distance(sSource, {f_x, f_y}) < SPOT_RADIUS_M)
                return true;
        return false;
    }
}
