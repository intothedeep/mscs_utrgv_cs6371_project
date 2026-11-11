#ifndef PHEROMONE_LOOP_FUNCTIONS_H
#define PHEROMONE_LOOP_FUNCTIONS_H

#include <argos3/core/simulator/loop_functions.h>
#include <argos3/core/simulator/entity/floor_entity.h>
#include <argos3/plugins/robots/foot-bot/simulator/footbot_entity.h>
#include <controllers/pheromone_forager/pheromone_forager.h>
#include "pheromone_grid.h"
#include "food_field.h"
#include "run_logger.h"
#include "id_arm.h"
#include <functional>
#include <memory>

using namespace argos;

/*
 * Owns all world state (DESIGN Figure 1): the grid, the food field and the
 * virtual sensor. Per tick: PreStep evaporates, handles pickup and drop and
 * writes each robot's reading. PostStep applies the deposit requests.
 */
class CPheromoneLoopFunctions : public CLoopFunctions
{
public:
    CPheromoneLoopFunctions();
    virtual ~CPheromoneLoopFunctions() {}

    virtual void Init(TConfigurationNode &t_tree);
    virtual void Reset();
    virtual void Destroy();
    virtual CColor GetFloorColor(const CVector2 &c_position_on_plane);
    virtual void PreStep();
    virtual void PostStep();
    virtual void PostExperiment();

private:
    using TRobotFn = std::function<void(CFootBotEntity &, CPheromoneForager &)>;
    void ForEachFootBot(const TRobotFn &f_visit);
    void UpdateRobotPreStep(CFootBotEntity &c_robot, CPheromoneForager &c_controller);
    /* One tick of the run log (pheromone_loop_functions_log.cpp). No-op without <logger>. */
    void LogStep();
    void OpenLogger(TConfigurationNode &t_node);
    void AssignDecoys();
    /* M6 ID arm (pheromone_loop_functions_id.cpp). It runs only when defense_mode is "id". */
    void ConfigureDefenseMode(TConfigurationNode &t_pheromone);
    void SetUpIdArm();
    void StepIdArm();

    enum EDefenseMode
    {
        MODE_LEGACY = 0, /* no defense_mode attribute: behaves as v4 */
        MODE_OFF,
        MODE_V3,
        MODE_V5,
        MODE_ID
    };

    CFloorEntity *m_pcFloor;
    std::unique_ptr<pheromone::CPheromoneGrid> m_pcGrid;
    pheromone::CFoodField m_cField;
    /* Read by the RunLogger (M2-05) and by detractor assignment (M3-01). */
    std::vector<pheromone::SPoint> m_vecActiveDecoys;

    Real m_fNestEdgeX;
    Real m_fProbeRadius;
    UInt32 m_unRepaintEvery; /* 0 = never: headless runs do not repaint */
    UInt32 m_unCollectedFood;

    pheromone::CRunLogger m_cLogger;
    bool m_bDecoysAssigned;
    UInt64 m_unWastedRobotTicks; /* integers, divided once: no float drift in the cumulative sum */

    EDefenseMode m_eMode;
    double m_fIdMargin;   /* travel-time margin, <pheromone id_margin>, D-048 D1 */
    double m_fHalfLifeS;
    std::string m_strDefenseLogPath; /* empty without <logger> */
    std::unique_ptr<pheromone::CIdArm> m_pcId; /* null unless defense_mode is "id" */
};

#endif
