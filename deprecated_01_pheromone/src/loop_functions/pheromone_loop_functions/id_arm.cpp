#include "id_arm.h"
#include <cmath>

namespace pheromone
{
    namespace
    {
        const double PI = 3.14159265358979323846;
        const char *SourceName(int n_source)
        {
            return n_source == SOURCE_PEAK ? "peak" : (n_source == SOURCE_FALLBACK ? "fallback" : "");
        }
    }

    CIdArm::CIdArm(CPheromoneGrid &c_grid, const SIdArmConfig &s_config)
        : m_pGrid(&c_grid), m_sConfig(s_config), m_cStore(s_config.expiryTicks),
          m_cDefense(s_config.params, m_cStore, static_cast<int>(s_config.ids.size()),
                     [this](int n_robot) { return ZeroOwned(n_robot); }),
          m_vecProbeOwner(s_config.ids.size(), -1), m_vecX(s_config.ids.size(), 0.0),
          m_vecY(s_config.ids.size(), 0.0), m_vecDepositing(s_config.ids.size(), false),
          m_vecLastDropLog(s_config.ids.size(), -1000000)
    {
        for (size_t i = 0; i < s_config.ids.size(); ++i)
            m_mapIndex[s_config.ids[i]] = static_cast<int>(i);
        if (!s_config.logPath.empty())
            m_cLog.Open(s_config.logPath);
    }

    int CIdArm::IndexOf(const std::string &str_id) const
    {
        auto cIt = m_mapIndex.find(str_id);
        return cIt == m_mapIndex.end() ? -1 : cIt->second;
    }

    void CIdArm::NoteProbeOwner(int n_robot, double f_x, double f_y, double f_yaw)
    {
        double fBest = -1.0;
        int nBestCell = -1;
        for (int i = -1; i < 8; ++i) /* i = -1: the cell under the robot, then probe 0 to 7 */
        {
            const double fAngle = f_yaw + i * PI / 4.0;
            const int nCell = (i < 0) ? CPheromoneGrid::CellIndexOf(f_x, f_y)
                                      : CPheromoneGrid::CellIndexOf(f_x + m_sConfig.probeRadiusM * std::cos(fAngle),
                                                                    f_y + m_sConfig.probeRadiusM * std::sin(fAngle));
            if (nCell < 0)
                continue;
            const double fValue = m_pGrid->ValueAt(LAYER_TRUE, nCell) + m_pGrid->ValueAt(LAYER_FALSE, nCell);
            if (fValue > fBest)
            {
                fBest = fValue;
                nBestCell = nCell;
            }
        }
        m_vecProbeOwner[n_robot] = (nBestCell < 0) ? -1
                                                    : m_cOwner.Dominant(nBestCell, m_pGrid->ValueAt(LAYER_TRUE, nBestCell),
                                                                        m_pGrid->ValueAt(LAYER_FALSE, nBestCell));
    }

    void CIdArm::NotePickup(int n_robot, double f_x, double f_y)
    {
        m_vecPickups.push_back({n_robot, f_x, f_y});
    }

    /* The first deposit of a run is the trail end. An isolated robot lays nothing (section 3.1). */
    void CIdArm::Deposit(int n_tick, int n_robot, ELayer e_layer, double f_x, double f_y, double f_amount, double f_min_x)
    {
        if (!m_vecDepositing[n_robot])
            m_cDefense.StartTrail(n_tick, n_robot, f_x, f_y);
        m_vecDepositing[n_robot] = true;
        if (m_cDefense.IsIsolated(n_robot))
        {
            if (n_tick - m_vecLastDropLog[n_robot] >= m_sConfig.params.ticksPerSecond)
            {
                m_vecLastDropLog[n_robot] = n_tick;
                WriteRow(m_cDefense.Snapshot(n_tick, n_robot, EV_DEPOSIT_DROPPED));
            }
            return;
        }
        std::vector<int> vecWon;
        m_pGrid->Deposit(e_layer, f_x, f_y, f_amount, f_min_x, &vecWon);
        for (int nCell : vecWon)
            m_cOwner.SetOwner(e_layer, nCell, n_robot);
    }

    void CIdArm::EndDepositRun(int n_robot)
    {
        m_vecDepositing[n_robot] = false;
    }

    void CIdArm::SetPosition(int n_robot, double f_x, double f_y)
    {
        m_vecX[n_robot] = f_x;
        m_vecY[n_robot] = f_y;
    }

    void CIdArm::NoteFollowStart(int n_robot)
    {
        m_vecFollowStarts.push_back(n_robot);
    }

    void CIdArm::NotePeak(int n_robot)
    {
        m_vecPeaks.push_back(n_robot);
    }

    /* Zeroes what the robot still owns. Counts only cells above theta_on: the older ones are
       owned on paper but have evaporated, so no robot could follow them. */
    int CIdArm::ZeroOwned(int n_robot)
    {
        int nLive = 0;
        for (const COwnerGrid::TCell &sCell : m_cOwner.ReleaseOwned(n_robot))
        {
            const ELayer eLayer = static_cast<ELayer>(sCell.first);
            if (m_pGrid->ValueAt(eLayer, sCell.second) > m_sConfig.liveValue)
                ++nLive;
            m_pGrid->ZeroCell(eLayer, sCell.second);
        }
        return nLive;
    }

    void CIdArm::WriteRow(const SDefenseEvent &s_event)
    {
        const int r = s_event.robot;
        SDefenseRow sRow;
        sRow.tick = static_cast<unsigned>(s_event.tick);
        sRow.robotId = m_sConfig.ids[r];
        sRow.role = m_sConfig.isHonest[r] ? "honest" : "detractor";
        sRow.event = EventName(s_event.event);
        sRow.checkId = s_event.checkId;
        sRow.strikes = s_event.strikes;
        sRow.isolated = s_event.isolated;
        sRow.groupSize = s_event.groupSize;
        sRow.trailCreator = s_event.trailCreator >= 0 ? m_sConfig.ids[s_event.trailCreator] : "";
        sRow.deadlineTick = s_event.deadlineTick;
        sRow.groupSource = SourceName(s_event.groupSource);
        sRow.cellsZeroed = s_event.cellsZeroed;
        sRow.x = m_vecX[r];
        sRow.y = m_vecY[r];
        m_cLog.Write(sRow);
    }

    /* Order inside one tick: open checks, confirm at peaks, resolve pickups, then deadlines and timers. */
    void CIdArm::Step(int n_tick)
    {
        for (int nRobot : m_vecFollowStarts)
            m_cDefense.OpenCheck(n_tick, nRobot, m_vecX[nRobot], m_vecY[nRobot], m_vecProbeOwner[nRobot]);
        for (int nRobot : m_vecPeaks)
            m_cDefense.ConfirmCheck(n_tick, nRobot, m_vecX[nRobot], m_vecY[nRobot]);
        for (const SPickup &sPickup : m_vecPickups)
            m_cDefense.OnPickup(n_tick, sPickup.robot, sPickup.x, sPickup.y);
        m_vecFollowStarts.clear();
        m_vecPeaks.clear();
        m_vecPickups.clear();
        m_cDefense.Advance(n_tick);
        for (const SDefenseEvent &sEvent : m_cDefense.TakeEvents())
            WriteRow(sEvent);
    }

    void CIdArm::WriteEndState(int n_tick)
    {
        for (size_t r = 0; r < m_sConfig.ids.size(); ++r)
            WriteRow(m_cDefense.Snapshot(n_tick, static_cast<int>(r), EV_END_STATE));
        m_cLog.Close();
    }
}
