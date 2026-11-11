#include "pheromone_loop_functions.h"
#include "run_info_reader.h"
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <argos3/core/utility/logging/argos_log.h>
#include <cmath>

/*
 * Run log glue (M2-05): reads the ground truth and the controller getters,
 * hands plain numbers to pheromone::CRunLogger. It never changes world state,
 * so logging cannot change a run (rules/measurement.md 2.4).
 */

namespace
{
    /* Bumped by hand with a CHANGELOG.md row (rules/measurement.md 2.1). */
    const char *CODE_VERSION = "v1";
    const char *STATE_NAMES[] = {"REST", "SEARCH", "FOLLOW", "END_SEARCH", "RETURN"};
    /* DESIGN 4.1: decoy radius 0.25 m + 0.25 m. */
    const Real WASTE_DECOY_RADIUS = 0.5f;
    const Real WASTE_FALSE_SHARE = 0.5f;
}

void CPheromoneLoopFunctions::OpenLogger(TConfigurationNode &t_node)
{
    pheromone::SRunInfo sInfo;
    if (!ReadRunInfo(t_node, sInfo))
        return;
    sInfo.codeVersion = CODE_VERSION;
    /* The whole layout is logged, both decoys drawn, so cells can be compared. */
    sInfo.sources = m_cField.Sources();
    sInfo.decoys = m_cField.Decoys();
    sInfo.decoysUsed = static_cast<unsigned>(m_vecActiveDecoys.size());
    sInfo.radius = pheromone::SPOT_RADIUS_M;
    m_cLogger.Open(sInfo);
}

void CPheromoneLoopFunctions::LogStep()
{
    if (!m_cLogger.IsOpen())
        return;
    const UInt32 unTicksPerSecond = static_cast<UInt32>(CPhysicsEngine::GetInverseSimulationClockTick() + 0.5f);
    const UInt32 unTick = GetSpace().GetSimulationClock();
    const bool bSampleRobots = (unTick % unTicksPerSecond) == 0; /* robots.csv: 1 row per robot per second */
    pheromone::STick sTick = {};

    ForEachFootBot([&](CFootBotEntity &c_robot, CPheromoneForager &c_controller)
                   {
        const SAnchor &sAnchor = c_robot.GetEmbodiedEntity().GetOriginAnchor();
        const Real fX = sAnchor.Position.GetX(), fY = sAnchor.Position.GetY();
        CRadians cYaw, cPitch, cRoll;
        sAnchor.Orientation.ToEulerAngles(cYaw, cPitch, cRoll);
        const std::string &strId = c_robot.GetId();
        const bool bHonest = strId.rfind("hb_", 0) == 0;
        const CPheromoneForager::EState eState = c_controller.GetState();

        /* Ground truth under the robot. 0 / 0 counts as 0. */
        const double fTrue = m_pcGrid->Value(pheromone::LAYER_TRUE, fX, fY);
        const double fFalse = m_pcGrid->Value(pheromone::LAYER_FALSE, fX, fY);
        const double fShare = (fTrue + fFalse > 0.0) ? fFalse / (fTrue + fFalse) : 0.0;

        if (bHonest)
        {
            ++sTick.states[eState];
            bool bNearDecoy = false;
            for (const pheromone::SPoint &sDecoy : m_vecActiveDecoys)
                bNearDecoy = bNearDecoy || std::hypot(fX - sDecoy.x, fY - sDecoy.y) <= WASTE_DECOY_RADIUS;
            /* Either condition counts the robot once for this tick (DESIGN 4.1). */
            if ((eState == CPheromoneForager::STATE_FOLLOW && fShare >= WASTE_FALSE_SHARE) ||
                (eState == CPheromoneForager::STATE_END_SEARCH && bNearDecoy))
                ++m_unWastedRobotTicks;
        }
        if (bSampleRobots)
            m_cLogger.LogRobot(unTick, strId, bHonest ? "honest" : "detractor", fX, fY,
                               ToDegrees(cYaw).GetValue(), STATE_NAMES[eState],
                               c_controller.IsCarrying() ? 1 : 0,
                               c_controller.GetPheromoneReading().here, fShare);
        if (c_controller.GetFollowStart())
            m_cLogger.LogEvent(unTick, strId, "follow_start", fX, fY);
        if (c_controller.GetPeakEvent() != CPheromoneForager::PEAK_NONE)
            m_cLogger.LogEvent(unTick, strId, "peak", fX, fY); });

    sTick.tick = unTick;
    sTick.food = m_unCollectedFood;
    sTick.wastedSeconds = static_cast<double>(m_unWastedRobotTicks) / unTicksPerSecond;
    sTick.pherTrue = m_pcGrid->LayerSum(pheromone::LAYER_TRUE);
    sTick.pherFalse = m_pcGrid->LayerSum(pheromone::LAYER_FALSE);
    sTick.suspects = 0; /* M3-02 fills this when the defense holds suspect points */
    m_cLogger.LogTick(sTick);
}
