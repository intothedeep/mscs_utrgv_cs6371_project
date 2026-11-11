#ifndef ID_ARM_H
#define ID_ARM_H

#include "defense_log.h"
#include "id_defense.h"
#include "owner_grid.h"
#include "pheromone_grid.h"
#include "trail_store.h"
#include <string>
#include <unordered_map>
#include <vector>

/*
 * The ID arm as the loop functions see it (DESIGN_M6 Figure 1): owner grid, trail store and the
 * defense, fed with plain numbers. Built only when defense_mode is "id". Pure: no simulator header.
 * Robots are known by an integer index, assigned from the id string at construction. The index
 * never carries the role. The role strings go to the sidecar only, as ground truth for analysis.
 */
namespace pheromone
{
    struct SIdArmConfig
    {
        SIdParams params;
        int expiryTicks = 0;        /* a record expires when its end deposit falls below theta_on (section 3.1) */
        double liveValue = 0.0;     /* theta_on: cells above it count as "zeroed" in the sidecar */
        double probeRadiusM = 0.15; /* the antenna ring of the sensor */
        std::vector<std::string> ids;
        std::vector<bool> isHonest; /* ground truth for the sidecar only */
        std::string logPath;        /* empty = no sidecar */
    };

    class CIdArm
    {
    public:
        CIdArm(CPheromoneGrid &c_grid, const SIdArmConfig &s_config);
        ~CIdArm() { m_cLog.Close(); }

        /* -1 when the id is unknown. */
        int IndexOf(const std::string &str_id) const;

        /* PreStep: the dominant owner of the strongest of the 9 probe cells (centre + 8 at the ring). */
        void NoteProbeOwner(int n_robot, double f_x, double f_y, double f_yaw);
        void NotePickup(int n_robot, double f_x, double f_y);
        /* PostStep. A deposit of one robot, after the nest test. */
        void Deposit(int n_tick, int n_robot, ELayer e_layer, double f_x, double f_y, double f_amount, double f_min_x);
        void EndDepositRun(int n_robot);
        void SetPosition(int n_robot, double f_x, double f_y);
        void NoteFollowStart(int n_robot);
        void NotePeak(int n_robot);
        /* After every deposit and flag of the tick: open, confirm, resolve, advance, write the sidecar. */
        void Step(int n_tick);
        void WriteEndState(int n_tick);

    private:
        struct SPickup
        {
            int robot;
            double x, y;
        };

        int ZeroOwned(int n_robot);
        void WriteRow(const SDefenseEvent &s_event);

        CPheromoneGrid *m_pGrid;
        SIdArmConfig m_sConfig;
        std::unordered_map<std::string, int> m_mapIndex;
        COwnerGrid m_cOwner;
        CTrailStore m_cStore;
        CIdDefense m_cDefense;
        CDefenseLog m_cLog;
        std::vector<int> m_vecProbeOwner;
        std::vector<double> m_vecX, m_vecY;
        std::vector<bool> m_vecDepositing;
        std::vector<int> m_vecLastDropLog;
        std::vector<int> m_vecFollowStarts, m_vecPeaks;
        std::vector<SPickup> m_vecPickups;
    };
}

#endif
