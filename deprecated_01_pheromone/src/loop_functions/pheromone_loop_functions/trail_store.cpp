#include "trail_store.h"
#include <algorithm>

namespace pheromone
{
    CTrailStore::CTrailStore(int n_expiry_ticks) : m_nExpiryTicks(n_expiry_ticks), m_nNextId(0) {}

    int CTrailStore::Add(int n_creator, double f_x, double f_y, int n_tick)
    {
        m_vecTrails.push_back({m_nNextId, n_creator, f_x, f_y, n_tick, 0.0});
        return m_nNextId++;
    }

    bool CTrailStore::Expire(int n_tick)
    {
        const size_t unBefore = m_vecTrails.size();
        m_vecTrails.erase(std::remove_if(m_vecTrails.begin(), m_vecTrails.end(),
                                         [&](const STrail &s_trail)
                                         { return n_tick - s_trail.startTick > m_nExpiryTicks; }),
                          m_vecTrails.end());
        return m_vecTrails.size() != unBefore;
    }

    void CTrailStore::RemoveCreator(int n_creator)
    {
        m_vecTrails.erase(std::remove_if(m_vecTrails.begin(), m_vecTrails.end(),
                                         [&](const STrail &s_trail)
                                         { return s_trail.creator == n_creator; }),
                          m_vecTrails.end());
    }

    bool CTrailStore::AddExtra(int n_id, double f_seconds)
    {
        for (STrail &sTrail : m_vecTrails)
            if (sTrail.id == n_id)
            {
                sTrail.extraS += f_seconds;
                return true;
            }
        return false;
    }

    const STrail *CTrailStore::Find(int n_id) const
    {
        for (const STrail &sTrail : m_vecTrails)
            if (sTrail.id == n_id)
                return &sTrail;
        return nullptr;
    }

    const STrail *CTrailStore::LatestOf(int n_creator) const
    {
        const STrail *pLatest = nullptr;
        for (const STrail &sTrail : m_vecTrails)
            if (sTrail.creator == n_creator && (!pLatest || sTrail.startTick >= pLatest->startTick))
                pLatest = &sTrail;
        return pLatest;
    }
}
