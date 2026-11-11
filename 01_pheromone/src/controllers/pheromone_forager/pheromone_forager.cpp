#include "pheromone_forager.h"
#include <argos3/core/utility/configuration/argos_configuration.h>
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <argos3/core/utility/logging/argos_log.h>


/****************************************/
/****************************************/

CPheromoneForager::SPheromoneReading::SPheromoneReading() : here(0.0f)
{
    for (size_t i = 0; i < NUM_PROBES; ++i)
        probe[i] = 0.0f;
}

CPheromoneForager::SDepositRequest::SDepositRequest() : active(false), amount(0.0f) {}

CPheromoneForager::SFoodData::SFoodData() : HasFoodItem(false), FoodItemIdx(0), TotalFoodItems(0) {}

void CPheromoneForager::SFoodData::Reset()
{
    HasFoodItem = false;
    FoodItemIdx = 0;
    TotalFoodItems = 0;
}

/****************************************/
/****************************************/

CPheromoneForager::CPheromoneForager() : m_pcWheels(NULL),
                                         m_pcLEDs(NULL),
                                         m_pcPositioning(NULL),
                                         m_pcProximity(NULL),
                                         m_pcRNG(NULL) {}

void CPheromoneForager::Init(TConfigurationNode &t_node)
{
    try
    {
        m_pcWheels = GetActuator<CCI_DifferentialSteeringActuator>("differential_steering");
        m_pcLEDs = GetActuator<CCI_LEDsActuator>("leds");
        /* The ground sensor is not requested: nest and pheromone use position (D-008). */
        m_pcPositioning = GetSensor<CCI_PositioningSensor>("positioning");
        m_pcProximity = GetSensor<CCI_FootBotProximitySensor>("footbot_proximity");
        /* Role picks the state machine. The detractor shares sensors, motion and params. */
        std::string strRole = "honest";
        GetNodeAttributeOrDefault(t_node, "role", strRole, strRole);
        if (strRole != "honest" && strRole != "detractor")
            THROW_ARGOSEXCEPTION("unknown role \"" << strRole << "\"");
        m_bDetractor = (strRole == "detractor");
        m_sParams.Init(t_node, CPhysicsEngine::GetInverseSimulationClockTick());
    }
    catch (CARGoSException &ex)
    {
        THROW_ARGOSEXCEPTION_NESTED("Error initializing pheromone_forager for robot \"" << GetId() << "\"", ex);
    }
    m_pcRNG = CRandom::CreateRNG("argos");
    Reset();
}

/* The decoy target is not reset: the loop functions set it once (D-009). */
void CPheromoneForager::Reset()
{
    m_sReading = SPheromoneReading();
    m_sSeen = SPheromoneReading();
    m_sDeposit = SDepositRequest();
    m_sFoodData.Reset();
    m_ePeakEvent = PEAK_NONE;
    m_bFollowStart = m_bDecoyReach = m_bSuspectAdd = m_bConeAbort = false;
    m_bPeakValid = false;
    m_vecSuspects.clear();
    m_eTurning = NO_TURN;
    m_unTripTicks = 0;
    m_unTauTicks = 0;
    m_bWasLaying = false;
    m_fHereEntry = 0.0f;
    Enter(STATE_REST);
}

/****************************************/
/****************************************/

void CPheromoneForager::ControlStep()
{
    /* Diagnostic: a def1 Qt run ends silently near tick 983. Name the robot, then rethrow. */
    try
    {
        ControlStepBody();
    }
    catch (std::exception &ex)
    {
        LOGERR << "[diag] ControlStep " << GetId() << " state " << m_eState << " suspects "
               << m_vecSuspects.size() << ": " << ex.what() << std::endl;
        throw;
    }
}

void CPheromoneForager::ControlStepBody()
{
    m_ePeakEvent = PEAK_NONE;
    m_bFollowStart = false;
    m_bDecoyReach = false;
    m_bSuspectAdd = false;
    m_bConeAbort = false;
    m_sDeposit.active = false;
    UpdatePose();
    MaskSuspects();

    /* tau counts from pickup (honest) or from leaving the decoy (detractor). */
    const bool bLaying = m_sFoodData.HasFoodItem || m_eState == STATE_RETURN_LAY;
    if (bLaying && !m_bWasLaying)
        m_unTauTicks = 0;
    if (bLaying)
        ++m_unTauTicks;
    m_bWasLaying = bLaying;

    ++m_unStateTicks;
    if (!m_bDetractor)
    {
        /* Pickup in SEARCH, FOLLOW or END_SEARCH ends the search. */
        if (m_sFoodData.HasFoodItem && m_eState != STATE_RETURN)
            Enter(STATE_RETURN);
        if (m_eState == STATE_SEARCH || m_eState == STATE_FOLLOW || m_eState == STATE_END_SEARCH)
        {
            ++m_unTripTicks;
            if (m_unTripTicks > m_sParams.SearchTicks)
                Enter(STATE_RETURN);
        }
    }

    switch (m_eState)
    {
    case STATE_REST: Rest(); break;
    case STATE_SEARCH: Search(); break;
    case STATE_FOLLOW: Follow(); break;
    case STATE_END_SEARCH: EndSearch(); break;
    case STATE_RETURN: Return(); break;
    case STATE_GO_DECOY: GoDecoy(); break;
    case STATE_WAIT_DECOY: WaitDecoy(); break;
    case STATE_RETURN_LAY: ReturnLay(); break;
    }
    RequestDeposit();
}

/****************************************/
/****************************************/

void CPheromoneForager::UpdatePose()
{
    const CCI_PositioningSensor::SReading &sReading = m_pcPositioning->GetReading();
    m_cPos.Set(sReading.Position.GetX(), sReading.Position.GetY());
    CRadians cZ, cY, cX;
    sReading.Orientation.ToEulerAngles(cZ, cY, cX);
    m_cYaw = cZ;
}

bool CPheromoneForager::IsInNest() const
{
    return m_cPos.GetX() < m_sParams.NestEdgeX;
}

/* Angle of a world point in the robot frame. */
CRadians CPheromoneForager::AngleTo(const CVector2 &c_point) const
{
    return ((c_point - m_cPos).Angle() - m_cYaw).SignedNormalize();
}

size_t CPheromoneForager::BestProbe() const
{
    size_t unBest = 0;
    for (size_t i = 1; i < NUM_PROBES; ++i)
        if (m_sSeen.probe[i] > m_sSeen.probe[unBest])
            unBest = i;
    return unBest;
}

/* Copied from hw5 search_deliver.cpp: sums proximity rays, points away. */
CVector2 CPheromoneForager::DiffusionVector(bool &b_collision)
{
    const CCI_FootBotProximitySensor::TReadings &tProx = m_pcProximity->GetReadings();
    CVector2 cDiffusion;
    for (size_t i = 0; i < tProx.size(); ++i)
        cDiffusion += CVector2(tProx[i].Value, tProx[i].Angle);
    if (m_sParams.GoStraightAngleRange.WithinMinBoundIncludedMaxBoundIncluded(cDiffusion.Angle()) &&
        cDiffusion.Length() < m_sParams.Delta)
    {
        b_collision = false;
        return CVector2::X;
    }
    b_collision = true;
    cDiffusion.Normalize();
    return -cDiffusion;
}

/* Copied from hw5 search_deliver.cpp: heading vector to wheel speeds. */
void CPheromoneForager::SetWheelSpeedsFromVector(const CVector2 &c_heading)
{
    CRadians cAngle = c_heading.Angle().SignedNormalize();
    Real fBase = Min<Real>(c_heading.Length(), m_sParams.MaxSpeed);
    if (m_eTurning == HARD_TURN && Abs(cAngle) <= m_sParams.SoftTurnOnAngleThreshold)
        m_eTurning = SOFT_TURN;
    if (m_eTurning == SOFT_TURN)
    {
        if (Abs(cAngle) > m_sParams.HardTurnOnAngleThreshold)
            m_eTurning = HARD_TURN;
        else if (Abs(cAngle) <= m_sParams.NoTurnAngleThreshold)
            m_eTurning = NO_TURN;
    }
    if (m_eTurning == NO_TURN)
    {
        if (Abs(cAngle) > m_sParams.HardTurnOnAngleThreshold)
            m_eTurning = HARD_TURN;
        else if (Abs(cAngle) > m_sParams.NoTurnAngleThreshold)
            m_eTurning = SOFT_TURN;
    }
    Real fSlow = fBase, fFast = fBase;
    if (m_eTurning == SOFT_TURN)
    {
        Real fFactor = (m_sParams.HardTurnOnAngleThreshold - Abs(cAngle)) / m_sParams.HardTurnOnAngleThreshold;
        fSlow = fBase - fBase * (1.0 - fFactor);
        fFast = fBase + fBase * (1.0 - fFactor);
    }
    else if (m_eTurning == HARD_TURN)
    {
        fSlow = -m_sParams.MaxSpeed;
        fFast = m_sParams.MaxSpeed;
    }
    if (cAngle > CRadians::ZERO)
        m_pcWheels->SetLinearVelocity(fSlow, fFast);
    else
        m_pcWheels->SetLinearVelocity(fFast, fSlow);
}

/* Obstacle avoidance wins; otherwise head for the wanted relative angle. */
void CPheromoneForager::SteerToward(const CRadians &c_relative_angle)
{
    bool bCollision;
    CVector2 cAvoid = DiffusionVector(bCollision);
    if (bCollision)
        SetWheelSpeedsFromVector(m_sParams.MaxSpeed * cAvoid);
    else
        SetWheelSpeedsFromVector(CVector2(m_sParams.MaxSpeed, c_relative_angle));
}

/* Correlated random walk: hold an absolute heading, rarely turn it. A
   relative random angle would circle, since the robot turns toward it. */
void CPheromoneForager::Wander()
{
    static const Real TURN_PROBABILITY = 0.03f; /* about one turn per 3 s */
    static const CRange<CRadians> TURN_RANGE(CRadians(-1.05f), CRadians(1.05f)); /* +-60 deg */
    bool bCollision;
    CVector2 cAvoid = DiffusionVector(bCollision);
    if (bCollision)
    {
        m_cWanderYaw = (m_cYaw + cAvoid.Angle()).SignedNormalize();
        SetWheelSpeedsFromVector(m_sParams.MaxSpeed * cAvoid);
        return;
    }
    if (m_pcRNG->Bernoulli(TURN_PROBABILITY))
        m_cWanderYaw = (m_cWanderYaw + m_pcRNG->Uniform(TURN_RANGE)).SignedNormalize();
    SetWheelSpeedsFromVector(CVector2(m_sParams.MaxSpeed, (m_cWanderYaw - m_cYaw).SignedNormalize()));
}

/****************************************/
/****************************************/

REGISTER_CONTROLLER(CPheromoneForager, "pheromone_forager_controller")
