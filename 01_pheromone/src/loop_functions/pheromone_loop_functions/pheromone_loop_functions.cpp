#include "pheromone_loop_functions.h"
#include <argos3/core/simulator/simulator.h>
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <argos3/core/utility/configuration/argos_configuration.h>
#include <argos3/core/utility/logging/argos_log.h>
#include <algorithm>
#include <cmath>

using pheromone::CPheromoneGrid;

namespace
{
    /* Peak strength at which the floor tint is full. Display only. */
    const Real PAINT_FULL = 250.0f;

    /* Role comes from the entity id prefix (DESIGN section 2.1). */
    bool IsHonest(const std::string &str_id) { return str_id.rfind("hb_", 0) == 0; }

    /* Tint white toward a pale colour: s = 1 gives (200, 255, 200) or (255, 200, 200). */
    CColor Tint(bool b_green, Real f_strength)
    {
        UInt8 unFade = static_cast<UInt8>(255.0f - 55.0f * std::min<Real>(1.0f, f_strength));
        return b_green ? CColor(unFade, 255, unFade) : CColor(255, unFade, unFade);
    }
}

/****************************************/
/****************************************/

CPheromoneLoopFunctions::CPheromoneLoopFunctions() : m_pcFloor(NULL),
                                                     m_fNestEdgeX(-1.0f),
                                                     m_fProbeRadius(0.15f),
                                                     m_unRepaintEvery(0),
                                                     m_unCollectedFood(0),
                                                     m_unWastedRobotTicks(0),
                                                     m_bDecoysAssigned(false) {}

void CPheromoneLoopFunctions::Init(TConfigurationNode &t_node)
{
    try
    {
        TConfigurationNode &tPh = GetNode(t_node, "pheromone");
        UInt32 unDetractors;
        Real fHalfLife;
        GetNodeAttribute(tPh, "n_det", unDetractors);
        GetNodeAttribute(tPh, "half_life_s", fHalfLife);
        GetNodeAttribute(tPh, "probe_radius_m", m_fProbeRadius);
        GetNodeAttribute(tPh, "nest_edge_x", m_fNestEdgeX);
        GetNodeAttribute(tPh, "repaint_every", m_unRepaintEvery);

        m_pcFloor = &GetSpace().GetFloorEntity();
        m_pcGrid.reset(new CPheromoneGrid(CPheromoneGrid::EvaporationFactor(
            fHalfLife, CPhysicsEngine::GetInverseSimulationClockTick())));

        /* Own random category, so the layout does not depend on how many
           robots draw from "argos". Not yet verified on beta59: the first
           build and smoke run check it (DESIGN section 3.1). The three
           cells of one seed then share sources and decoy spots. */
        CRandom::CreateCategory("layout", CSimulator::GetInstance().GetRandomSeed());
        CRandom::CRNG *pcLayoutRNG = CRandom::CreateRNG("layout");
        m_cField.Draw([pcLayoutRNG](double f_min, double f_max)
                      { return static_cast<double>(pcLayoutRNG->Uniform(CRange<Real>(f_min, f_max))); });
        m_vecActiveDecoys = m_cField.ActiveDecoys(unDetractors);
        OpenLogger(t_node);
    }
    catch (CARGoSException &ex)
    {
        THROW_ARGOSEXCEPTION_NESTED("Error parsing loop functions!", ex);
    }
    catch (std::exception &ex)
    {
        /* food_field and run_logger throw std exceptions. */
        THROW_ARGOSEXCEPTION("Error in loop functions: " << ex.what());
    }
}

/* The layout stays: a GUI reset replays the same sources and decoys. */
void CPheromoneLoopFunctions::Reset()
{
    /* A GUI reset would append to the open run files, so close the log first (manifest: complete false). */
    m_cLogger.Close();
    m_pcGrid->Clear();
    m_unCollectedFood = 0;
    m_unWastedRobotTicks = 0;
}

void CPheromoneLoopFunctions::Destroy()
{
    m_cLogger.Close(); /* idempotent: PostExperiment may have closed it already */
}

/****************************************/
/****************************************/

/* Display only. The ground sensor is never read for nest or pheromone (D-008). */
CColor CPheromoneLoopFunctions::GetFloorColor(const CVector2 &c_position_on_plane)
{
    Real fX = c_position_on_plane.GetX(), fY = c_position_on_plane.GetY();
    if (fX < m_fNestEdgeX)
        return CColor::GRAY50;
    if (m_cField.IsOnSource(fX, fY))
        return CColor::BLACK;
    if (!m_pcGrid)
        return CColor::WHITE;
    Real fTrue = m_pcGrid->Value(pheromone::LAYER_TRUE, fX, fY);
    Real fFalse = m_pcGrid->Value(pheromone::LAYER_FALSE, fX, fY);
    if (fTrue <= 0.0f && fFalse <= 0.0f)
        return CColor::WHITE;
    return (fTrue >= fFalse) ? Tint(true, fTrue / PAINT_FULL) : Tint(false, fFalse / PAINT_FULL);
}

/****************************************/
/****************************************/

void CPheromoneLoopFunctions::ForEachFootBot(const TRobotFn &f_visit)
{
    CSpace::TMapPerType &mapFootBots = GetSpace().GetEntitiesByType("foot-bot");
    for (auto &cItem : mapFootBots)
    {
        CFootBotEntity &cFootBot = *any_cast<CFootBotEntity *>(cItem.second);
        f_visit(cFootBot, dynamic_cast<CPheromoneForager &>(cFootBot.GetControllableEntity().GetController()));
    }
}

void CPheromoneLoopFunctions::UpdateRobotPreStep(CFootBotEntity &c_robot, CPheromoneForager &c_controller)
{
    const SAnchor &sAnchor = c_robot.GetEmbodiedEntity().GetOriginAnchor();
    Real fX = sAnchor.Position.GetX(), fY = sAnchor.Position.GetY();
    CRadians cYaw, cPitch, cRoll;
    sAnchor.Orientation.ToEulerAngles(cYaw, cPitch, cRoll);

    /* Nest test by position, never by floor colour (D-008). */
    CPheromoneForager::SFoodData &sFood = c_controller.GetFoodData();
    if (IsHonest(c_robot.GetId()))
    {
        if (sFood.HasFoodItem && fX < m_fNestEdgeX)
        {
            sFood.HasFoodItem = false;
            ++sFood.TotalFoodItems;
            ++m_unCollectedFood;
            m_cLogger.LogEvent(GetSpace().GetSimulationClock(), c_robot.GetId(), "drop", fX, fY);
        }
        else if (!sFood.HasFoodItem && fX >= m_fNestEdgeX && m_cField.IsOnSource(fX, fY))
        {
            sFood.HasFoodItem = true; /* the source stays full */
            m_cLogger.LogEvent(GetSpace().GetSimulationClock(), c_robot.GetId(), "pickup", fX, fY);
        }
    }

    /* Virtual sensor: centre plus 8 probes, 45 degrees apart from the heading. */
    CPheromoneForager::SPheromoneReading &sReading = c_controller.GetPheromoneReading();
    sReading.here = m_pcGrid->Probe(fX, fY);
    for (size_t i = 0; i < CPheromoneForager::NUM_PROBES; ++i)
    {
        Real fAngle = cYaw.GetValue() + static_cast<Real>(i) * ARGOS_PI / 4.0f;
        sReading.probe[i] = m_pcGrid->Probe(fX + m_fProbeRadius * std::cos(fAngle),
                                            fY + m_fProbeRadius * std::sin(fAngle));
    }
}

/* D-009: detractor j lures to active decoy j mod n_decoys (d = 1, 2, 4 -> decoys 1, 2, 2).
   Done in the first PreStep, not in Init: that the controller objects already exist when
   the loop functions Init runs is not verified on beta59. */
void CPheromoneLoopFunctions::AssignDecoys()
{
    size_t unDetractor = 0;
    ForEachFootBot([&](CFootBotEntity &c_robot, CPheromoneForager &c_controller)
                   {
        if (IsHonest(c_robot.GetId()))
            return;
        if (m_vecActiveDecoys.empty())
            THROW_ARGOSEXCEPTION("detractor " << c_robot.GetId() << " has no decoy: n_det is 0");
        const pheromone::SPoint &sDecoy = m_vecActiveDecoys[unDetractor++ % m_vecActiveDecoys.size()];
        c_controller.SetDecoy(CVector2(sDecoy.x, sDecoy.y)); });
    m_bDecoysAssigned = true;
}

void CPheromoneLoopFunctions::PreStep()
{
    if (!m_bDecoysAssigned)
        AssignDecoys();
    m_pcGrid->Evaporate();
    ForEachFootBot([this](CFootBotEntity &c_robot, CPheromoneForager &c_controller)
                   { UpdateRobotPreStep(c_robot, c_controller); });
}

void CPheromoneLoopFunctions::PostStep()
{
    ForEachFootBot([this](CFootBotEntity &c_robot, CPheromoneForager &c_controller)
                   {
        CPheromoneForager::SDepositRequest &sRequest = c_controller.GetDepositRequest();
        const CVector3 &cPos = c_robot.GetEmbodiedEntity().GetOriginAnchor().Position;
        /* hb_ writes the true layer, dt_ the false layer. No deposit in the nest. */
        if (sRequest.active && cPos.GetX() >= m_fNestEdgeX)
            m_pcGrid->Deposit(IsHonest(c_robot.GetId()) ? pheromone::LAYER_TRUE : pheromone::LAYER_FALSE,
                              cPos.GetX(), cPos.GetY(), sRequest.amount, m_fNestEdgeX);
        sRequest.active = false; });
    LogStep(); /* after every deposit, so the layer sums are final for this tick */
    if (m_unRepaintEvery > 0 && GetSpace().GetSimulationClock() % m_unRepaintEvery == 0)
        m_pcFloor->SetChanged();
}

void CPheromoneLoopFunctions::PostExperiment()
{
    m_cLogger.Close();
    LOG << "food_collected " << m_unCollectedFood << std::endl;
}

/****************************************/
/****************************************/

REGISTER_LOOP_FUNCTIONS(CPheromoneLoopFunctions, "pheromone_loop_functions")
