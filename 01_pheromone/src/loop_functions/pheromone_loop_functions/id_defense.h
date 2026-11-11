#ifndef ID_DEFENSE_H
#define ID_DEFENSE_H

#include "trail_clusters.h"
#include "trail_store.h"
#include <functional>
#include <utility>
#include <vector>

/*
 * The ID-based defense (DESIGN_M6 sections 3.2 to 3.4): travel-time checks, strikes, isolation,
 * release. Pure: no simulator header, no random draw. It sees (robot index, position, tick)
 * and never the layer, the role or the entity id (hard rule of section 2).
 * Values the paper does not state are the defaults below (Table 3). They are frozen in
 * prereg/defense_id_arm.md. The margin is the only one the run tool sets.
 */
namespace pheromone
{
    struct SIdParams
    {
        double margin = 1.5;           /* travel-time margin, D-048 D1 */
        double speedMps = 0.10;        /* reference speed = max_speed */
        double endSeconds = 15.0;      /* t_end, the END_SEARCH time. The glue reads the real value */
        double epsM = 0.3;             /* clustering radius = END_SEARCH radius */
        int minPts = 2;                /* paper value */
        double peakRadiusM = 0.5;      /* peak-match radius */
        double lateRadiusM = 0.5;      /* late-return radius */
        double feedbackGain = 0.5;     /* estimate update gain */
        int strikeLimit = 5;           /* paper value */
        double isolationSeconds = 120.0;
        int ticksPerSecond = 10;
    };

    enum EDefenseEvent
    {
        EV_CHECK_OPEN = 0, EV_CHECK_CONFIRM, EV_CHECK_ONTIME, EV_CHECK_MISS, EV_STRIKE, EV_LATE_RETURN,
        EV_STRIKE_REMOVED, EV_ISOLATE, EV_RELEASE_LATE, EV_RELEASE_TIMER, EV_DEPOSIT_DROPPED, EV_END_STATE
    };
    /* The text of the `event` column of defense_log.csv. */
    const char *EventName(EDefenseEvent e_event);

    enum EGroupSource { SOURCE_NONE = 0, SOURCE_PEAK, SOURCE_FALLBACK };

    /* One row of defense_log.csv before the glue adds role, ids and position. */
    struct SDefenseEvent
    {
        int tick, robot;
        EDefenseEvent event;
        int checkId, strikes, isolated, groupSize;
        int trailCreator; /* robot index, -1 = none */
        int deadlineTick, groupSource, cellsZeroed;
    };

    class CIdDefense
    {
    public:
        /* f_zero_cells(robot) zeroes the cells the robot owns and returns how many it zeroed. */
        using TZeroFn = std::function<int(int)>;
        CIdDefense(const SIdParams &s_params, CTrailStore &c_store, int n_robots, TZeroFn f_zero_cells);

        bool IsIsolated(int n_robot) const { return m_vecIsolatedUntil[n_robot] >= 0; }
        int Strikes(int n_robot) const { return m_vecStrikes[n_robot]; }

        /* A deposit run starts. No record for an isolated creator (section 3.1 rule 4). */
        void StartTrail(int n_tick, int n_robot, double f_x, double f_y);
        /* follow_start: n_owner is the dominant owner of the strongest probe cell, -1 = none. */
        void OpenCheck(int n_tick, int n_robot, double f_x, double f_y, int n_owner);
        /* First peak of a follow. */
        void ConfirmCheck(int n_tick, int n_robot, double f_x, double f_y);
        void OnPickup(int n_tick, int n_robot, double f_x, double f_y);
        /* Once per tick, after every event of the tick: expiry, missed deadlines, isolation timers. */
        void Advance(int n_tick);

        std::vector<SDefenseEvent> TakeEvents();
        /* A row for the state of one robot, for the glue's own rows. */
        SDefenseEvent Snapshot(int n_tick, int n_robot, EDefenseEvent e_event) const;

    private:
        struct SCheck
        {
            int id, follower;
            int provTrailId, provCreator;
            int openTick, deadlineTick;
            double estimateS;
            bool isAwaiting;                 /* the deadline passed and the group was struck */
            bool isConfirmed;
            int anchorTrailId;               /* the trail whose cluster is "the assigned cluster" */
            double anchorX, anchorY;
            int groupSource;
            std::vector<int> struck;         /* S: creators struck at the miss */
            std::vector<std::pair<double, double>> clusterEnds; /* C at the miss */
        };

        const SGroups &Groups();
        int EndOfTrail(int n_trail_id, double f_x, double f_y);
        void Miss(SCheck &s_check, int n_tick);
        void LateReturn(const SCheck &s_check, int n_tick);
        void Isolate(int n_robot, int n_tick, const SCheck &s_check);
        void Release(int n_robot, int n_tick, EDefenseEvent e_event, const SCheck *p_check, int n_group_size);
        void Emit(int n_tick, int n_robot, EDefenseEvent e_event, const SCheck *p_check,
                  int n_group_size, int n_cells_zeroed);

        SIdParams m_sParams;
        CTrailStore &m_cStore;
        TZeroFn m_fZeroCells;
        std::vector<int> m_vecStrikes;
        std::vector<int> m_vecIsolatedUntil; /* tick the isolation ends, -1 = not isolated */
        std::vector<SCheck> m_vecChecks;
        int m_nNextCheckId;
        SGroups m_sGroups;
        bool m_bGroupsValid;
        std::vector<SDefenseEvent> m_vecEvents;
    };
}

#endif
