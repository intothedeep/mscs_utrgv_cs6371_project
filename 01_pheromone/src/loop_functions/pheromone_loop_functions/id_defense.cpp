#include "id_defense.h"
#include <cmath>

namespace pheromone
{
    const char *EventName(EDefenseEvent e_event)
    {
        static const char *const NAMES[] = {"check_open", "check_confirm", "check_ontime", "check_miss", "strike",
                                            "late_return", "strike_removed", "isolate", "release_late",
                                            "release_timer", "deposit_dropped", "end_state"};
        return NAMES[e_event];
    }

    CIdDefense::CIdDefense(const SIdParams &s_params, CTrailStore &c_store, int n_robots, TZeroFn f_zero_cells)
        : m_sParams(s_params), m_cStore(c_store), m_fZeroCells(std::move(f_zero_cells)),
          m_vecStrikes(n_robots, 0), m_vecIsolatedUntil(n_robots, -1), m_nNextCheckId(0), m_bGroupsValid(false) {}

    /* On demand and cached until the store changes (section 3.3 step 5). */
    const SGroups &CIdDefense::Groups()
    {
        if (!m_bGroupsValid)
        {
            m_sGroups = GroupTrails(m_cStore.Active(), m_sParams.epsM, m_sParams.minPts);
            m_bGroupsValid = true;
        }
        return m_sGroups;
    }

    /* Index in Active() of the end of this trail. The record may be gone (creator isolated,
       or expired): then the nearest live end within eps of the old position, else -1. */
    int CIdDefense::EndOfTrail(int n_trail_id, double f_x, double f_y)
    {
        const std::vector<STrail> &vecEnds = m_cStore.Active();
        double fBest = m_sParams.epsM;
        int nBest = -1;
        for (size_t i = 0; i < vecEnds.size(); ++i)
        {
            if (vecEnds[i].id == n_trail_id)
                return static_cast<int>(i);
            const double fDist = std::hypot(vecEnds[i].x - f_x, vecEnds[i].y - f_y);
            if (fDist <= fBest)
            {
                fBest = fDist;
                nBest = static_cast<int>(i);
            }
        }
        return nBest;
    }

    void CIdDefense::Emit(int n_tick, int n_robot, EDefenseEvent e_event, const SCheck *p_check,
                          int n_group_size, int n_cells_zeroed)
    {
        SDefenseEvent sEvent = Snapshot(n_tick, n_robot, e_event);
        sEvent.checkId = p_check ? p_check->id : -1;
        sEvent.groupSize = n_group_size;
        sEvent.trailCreator = p_check ? p_check->provCreator : -1;
        sEvent.deadlineTick = p_check ? p_check->deadlineTick : -1;
        sEvent.groupSource = p_check ? p_check->groupSource : SOURCE_NONE;
        sEvent.cellsZeroed = n_cells_zeroed;
        m_vecEvents.push_back(sEvent);
    }

    SDefenseEvent CIdDefense::Snapshot(int n_tick, int n_robot, EDefenseEvent e_event) const
    {
        return {n_tick, n_robot, e_event, -1, m_vecStrikes[n_robot], IsIsolated(n_robot) ? 1 : 0, 0, -1, -1,
                SOURCE_NONE, 0};
    }

    std::vector<SDefenseEvent> CIdDefense::TakeEvents()
    {
        std::vector<SDefenseEvent> vecOut;
        vecOut.swap(m_vecEvents);
        return vecOut;
    }

    void CIdDefense::StartTrail(int n_tick, int n_robot, double f_x, double f_y)
    {
        if (IsIsolated(n_robot))
            return;
        m_cStore.Add(n_robot, f_x, f_y, n_tick);
        m_bGroupsValid = false;
    }

    /* Figure 2: the provisional trail is the latest record of the dominant owner of the strongest
       probe cell. The deadline is t0 + margin x (distance / speed + t_end + est_extra_s). */
    void CIdDefense::OpenCheck(int n_tick, int n_robot, double f_x, double f_y, int n_owner)
    {
        if (n_owner < 0)
            return;
        const STrail *pTrail = m_cStore.LatestOf(n_owner);
        if (!pTrail)
            return;
        for (const SCheck &sOpen : m_vecChecks)
            if (!sOpen.isAwaiting && sOpen.follower == n_robot && sOpen.provTrailId == pTrail->id)
                return; /* a re-follow of the same trail opens no new check */
        const double fEstimate = std::hypot(f_x - pTrail->x, f_y - pTrail->y) / m_sParams.speedMps +
                                 m_sParams.endSeconds + pTrail->extraS;
        SCheck sCheck;
        sCheck.id = m_nNextCheckId++;
        sCheck.follower = n_robot;
        sCheck.provTrailId = pTrail->id;
        sCheck.provCreator = pTrail->creator;
        sCheck.openTick = n_tick;
        sCheck.estimateS = fEstimate;
        sCheck.deadlineTick = n_tick + static_cast<int>(std::llround(m_sParams.margin * fEstimate *
                                                                     m_sParams.ticksPerSecond));
        sCheck.isAwaiting = sCheck.isConfirmed = false;
        sCheck.anchorTrailId = pTrail->id;
        sCheck.anchorX = pTrail->x;
        sCheck.anchorY = pTrail->y;
        sCheck.groupSource = SOURCE_NONE;
        m_vecChecks.push_back(sCheck);
        Emit(n_tick, n_robot, EV_CHECK_OPEN, &m_vecChecks.back(), 0, 0);
    }

    /* The peak tells which trail end the follower reached: the nearest end within the peak radius.
       No such end: the provisional trail stays the anchor. */
    void CIdDefense::ConfirmCheck(int n_tick, int n_robot, double f_x, double f_y)
    {
        SCheck *pCheck = nullptr;
        for (auto cIt = m_vecChecks.rbegin(); cIt != m_vecChecks.rend() && !pCheck; ++cIt)
            if (cIt->follower == n_robot && !cIt->isAwaiting && !cIt->isConfirmed)
                pCheck = &*cIt;
        if (!pCheck)
            return;
        pCheck->isConfirmed = true;
        pCheck->groupSource = SOURCE_FALLBACK;
        double fBest = m_sParams.peakRadiusM;
        for (const STrail &sEnd : m_cStore.Active())
        {
            const double fDist = std::hypot(sEnd.x - f_x, sEnd.y - f_y);
            if (fDist <= fBest)
            {
                fBest = fDist;
                pCheck->anchorTrailId = sEnd.id;
                pCheck->anchorX = sEnd.x;
                pCheck->anchorY = sEnd.y;
                pCheck->groupSource = SOURCE_PEAK;
            }
        }
        int nGroupSize = 0;
        const int nEnd = EndOfTrail(pCheck->anchorTrailId, pCheck->anchorX, pCheck->anchorY);
        if (nEnd >= 0)
            nGroupSize = static_cast<int>(Groups().creators[Groups().groupOfEnd[nEnd]].size());
        Emit(n_tick, n_robot, EV_CHECK_CONFIRM, pCheck, nGroupSize, 0);
    }

    /* Any pickup before the deadline closes the check. After a miss, only a pickup near the assigned
       cluster is a late return (D-048 D5). The next pickup elsewhere drops the waiting check. */
    void CIdDefense::OnPickup(int n_tick, int n_robot, double f_x, double f_y)
    {
        std::vector<SCheck> vecKeep;
        for (const SCheck &sCheck : m_vecChecks)
        {
            if (sCheck.follower != n_robot)
            {
                vecKeep.push_back(sCheck);
                continue;
            }
            if (!sCheck.isAwaiting)
            {
                Emit(n_tick, n_robot, EV_CHECK_ONTIME, &sCheck, 0, 0);
                continue;
            }
            bool bNear = false;
            for (const auto &sEnd : sCheck.clusterEnds)
                bNear = bNear || std::hypot(sEnd.first - f_x, sEnd.second - f_y) <= m_sParams.lateRadiusM;
            if (bNear)
                LateReturn(sCheck, n_tick);
        }
        m_vecChecks.swap(vecKeep);
    }

    void CIdDefense::LateReturn(const SCheck &s_check, int n_tick)
    {
        const double fMeasured = static_cast<double>(n_tick - s_check.openTick) / m_sParams.ticksPerSecond;
        m_cStore.AddExtra(s_check.provTrailId, m_sParams.feedbackGain * (fMeasured - s_check.estimateS));
        Emit(n_tick, s_check.follower, EV_LATE_RETURN, &s_check, static_cast<int>(s_check.struck.size()), 0);
        for (int nCreator : s_check.struck)
        {
            if (IsIsolated(nCreator))
                Release(nCreator, n_tick, EV_RELEASE_LATE, &s_check, static_cast<int>(s_check.struck.size()));
            else if (m_vecStrikes[nCreator] > 0)
            {
                --m_vecStrikes[nCreator];
                Emit(n_tick, nCreator, EV_STRIKE_REMOVED, &s_check, static_cast<int>(s_check.struck.size()), 0);
            }
        }
    }

    void CIdDefense::Release(int n_robot, int n_tick, EDefenseEvent e_event, const SCheck *p_check, int n_group_size)
    {
        m_vecIsolatedUntil[n_robot] = -1;
        m_vecStrikes[n_robot] = 0; /* a fresh start (Table 3) */
        Emit(n_tick, n_robot, e_event, p_check, n_group_size, 0);
    }

    /* Zero the owned cells, drop the records, start the timer. The strikes stay at the limit. */
    void CIdDefense::Isolate(int n_robot, int n_tick, const SCheck &s_check)
    {
        m_vecIsolatedUntil[n_robot] = n_tick + static_cast<int>(std::llround(m_sParams.isolationSeconds *
                                                                             m_sParams.ticksPerSecond));
        const int nZeroed = m_fZeroCells(n_robot);
        m_cStore.RemoveCreator(n_robot);
        m_bGroupsValid = false;
        Emit(n_tick, n_robot, EV_ISOLATE, &s_check, 0, nZeroed);
    }

    /* The deadline passed with no pickup: strike every non-isolated creator in the group of the
       anchor's cluster (TAROS p. 311), and keep the check as "awaiting" with its cluster ends. */
    void CIdDefense::Miss(SCheck &s_check, int n_tick)
    {
        s_check.isAwaiting = true;
        if (s_check.groupSource == SOURCE_NONE)
            s_check.groupSource = SOURCE_FALLBACK;
        const int nEnd = EndOfTrail(s_check.anchorTrailId, s_check.anchorX, s_check.anchorY);
        if (nEnd < 0)
        {
            s_check.clusterEnds.emplace_back(s_check.anchorX, s_check.anchorY);
            Emit(n_tick, s_check.follower, EV_CHECK_MISS, &s_check, 0, 0);
            return;
        }
        const SGroups &sGroups = Groups();
        const std::vector<STrail> &vecEnds = m_cStore.Active();
        for (size_t i = 0; i < vecEnds.size(); ++i)
            if (sGroups.clusterOfEnd[i] == sGroups.clusterOfEnd[nEnd])
                s_check.clusterEnds.emplace_back(vecEnds[i].x, vecEnds[i].y);
        const std::vector<int> vecCreators = sGroups.creators[sGroups.groupOfEnd[nEnd]]; /* a copy: Isolate() regroups */
        Emit(n_tick, s_check.follower, EV_CHECK_MISS, &s_check, static_cast<int>(vecCreators.size()), 0);
        for (int nCreator : vecCreators)
        {
            if (IsIsolated(nCreator))
                continue;
            ++m_vecStrikes[nCreator];
            s_check.struck.push_back(nCreator);
            Emit(n_tick, nCreator, EV_STRIKE, &s_check, static_cast<int>(vecCreators.size()), 0);
            if (m_vecStrikes[nCreator] >= m_sParams.strikeLimit)
                Isolate(nCreator, n_tick, s_check);
        }
    }

    void CIdDefense::Advance(int n_tick)
    {
        if (m_cStore.Expire(n_tick))
            m_bGroupsValid = false;
        for (SCheck &sCheck : m_vecChecks)
            if (!sCheck.isAwaiting && n_tick > sCheck.deadlineTick)
                Miss(sCheck, n_tick);
        for (size_t r = 0; r < m_vecIsolatedUntil.size(); ++r)
            if (m_vecIsolatedUntil[r] >= 0 && n_tick >= m_vecIsolatedUntil[r])
                Release(static_cast<int>(r), n_tick, EV_RELEASE_TIMER, nullptr, 0);
    }
}
