#include "pheromone_loop_functions.h"
#include <argos3/core/simulator/simulator.h>
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <argos3/core/utility/configuration/argos_configuration.h>
#include <cmath>

/*
 * Glue of the ID arm (M6, DESIGN_M6 sections 2 and 6): the defense_mode attribute, its guard,
 * and the calls into pheromone::CIdArm. Nothing here runs unless defense_mode is "id", except
 * the guard, which only reads. It draws no random number and never changes the controller.
 */

namespace
{
    TConfigurationNode &ControllerParams()
    {
        return GetNode(GetNode(GetNode(CSimulator::GetInstance().GetConfigurationRoot(), "controllers"),
                               "pheromone_forager_controller"),
                       "params");
    }
}

/* DESIGN_M6 Table 5. An absent attribute is "legacy": the run behaves as v4 and saved .argos files load.
   The manifest keeps defense = 0 only for off. The controller suspect rule must match the mode. */
void CPheromoneLoopFunctions::ConfigureDefenseMode(TConfigurationNode &t_pheromone)
{
    std::string strMode = "legacy";
    GetNodeAttributeOrDefault(t_pheromone, "defense_mode", strMode, strMode);
    if (strMode == "legacy")
        return;
    bool bWantEnabled = true;
    UInt32 unWantDefense = 1;
    if (strMode == "off")
    {
        m_eMode = MODE_OFF;
        bWantEnabled = false;
        unWantDefense = 0;
    }
    else if (strMode == "v3")
        m_eMode = MODE_V3;
    else if (strMode == "v5")
        m_eMode = MODE_V5;
    else if (strMode == "id")
    {
        m_eMode = MODE_ID;
        bWantEnabled = false; /* the id arm turns the controller suspect rule off: no mixed defense */
    }
    else
        THROW_ARGOSEXCEPTION("unknown defense_mode \"" << strMode << "\"");
    bool bEnabled;
    UInt32 unDefense;
    GetNodeAttribute(GetNode(ControllerParams(), "defense"), "enabled", bEnabled);
    GetNodeAttribute(t_pheromone, "defense", unDefense);
    if (bEnabled != bWantEnabled || unDefense != unWantDefense)
        THROW_ARGOSEXCEPTION("defense_mode \"" << strMode << "\" needs defense=" << unWantDefense
                                               << " and controller defense enabled=" << bWantEnabled);
    GetNodeAttributeOrDefault(t_pheromone, "id_margin", m_fIdMargin, m_fIdMargin);
}

/* In the first PreStep, like AssignDecoys(): the robot entities are known then. */
void CPheromoneLoopFunctions::SetUpIdArm()
{
    pheromone::SIdArmConfig sConfig;
    ForEachFootBot([&](CFootBotEntity &c_robot, CPheromoneForager &)
                   {
        sConfig.ids.push_back(c_robot.GetId());
        sConfig.isHonest.push_back(c_robot.GetId().rfind("hb_", 0) == 0); /* sidecar ground truth only */ });
    TConfigurationNode &tPh = GetNode(ControllerParams(), "pheromone");
    double fAMax, fThetaOn, fEndSeconds;
    GetNodeAttribute(tPh, "a_max", fAMax);
    GetNodeAttribute(tPh, "theta_on", fThetaOn);
    GetNodeAttribute(tPh, "t_end", fEndSeconds);
    const double fTicksPerSecond = CPhysicsEngine::GetInverseSimulationClockTick();
    sConfig.params.margin = m_fIdMargin;
    sConfig.params.endSeconds = fEndSeconds;
    sConfig.params.ticksPerSecond = static_cast<int>(fTicksPerSecond + 0.5);
    /* The end deposit (a_max) decays below theta_on after half_life x log2(a_max / theta_on) seconds. */
    sConfig.expiryTicks = static_cast<int>(std::llround(m_fHalfLifeS * std::log2(fAMax / fThetaOn) * fTicksPerSecond));
    sConfig.liveValue = fThetaOn;
    sConfig.probeRadiusM = m_fProbeRadius;
    sConfig.logPath = m_strDefenseLogPath;
    try
    {
        m_pcId.reset(new pheromone::CIdArm(*m_pcGrid, sConfig));
    }
    catch (std::exception &ex)
    {
        THROW_ARGOSEXCEPTION("Error in the ID arm: " << ex.what());
    }
}

/* PostStep, after every deposit of the tick: hand over positions and controller flags, then step. */
void CPheromoneLoopFunctions::StepIdArm()
{
    ForEachFootBot([this](CFootBotEntity &c_robot, CPheromoneForager &c_controller)
                   {
        const CVector3 &cPos = c_robot.GetEmbodiedEntity().GetOriginAnchor().Position;
        const int nRobot = m_pcId->IndexOf(c_robot.GetId());
        m_pcId->SetPosition(nRobot, cPos.GetX(), cPos.GetY());
        if (c_controller.GetFollowStart())
            m_pcId->NoteFollowStart(nRobot);
        if (c_controller.GetPeakEvent() != CPheromoneForager::PEAK_NONE)
            m_pcId->NotePeak(nRobot); });
    m_pcId->Step(static_cast<int>(GetSpace().GetSimulationClock()));
}
