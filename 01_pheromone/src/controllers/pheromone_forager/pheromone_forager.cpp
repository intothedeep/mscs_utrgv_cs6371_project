#include "pheromone_forager.h"
#include <argos3/core/utility/configuration/argos_configuration.h>
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <limits>

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

CPheromoneForager::SParams::SParams() : GoStraightAngleRange(CRadians(-1.0f), CRadians(1.0f)) {}

/* Seconds in the XML become ticks here, so the controller never hard-codes
   10 ticks per second. The clock tick is set by <experiment> before any
   controller is initialised (core/simulator/physics_engine/physics_engine.h). */
static UInt32 ToTicks(TConfigurationNode &t_node, const char *pch_name, Real f_tps)
{
    Real fSeconds;
    GetNodeAttribute(t_node, pch_name, fSeconds);
    return static_cast<UInt32>(fSeconds * f_tps + 0.5f);
}

void CPheromoneForager::SParams::Init(TConfigurationNode &t_params, Real f_tps)
{
    TConfigurationNode &tDiff = GetNode(t_params, "diffusion");
    CRange<CDegrees> cStraight(CDegrees(-10.0f), CDegrees(10.0f));
    GetNodeAttribute(tDiff, "go_straight_angle_range", cStraight);
    GoStraightAngleRange.Set(ToRadians(cStraight.GetMin()), ToRadians(cStraight.GetMax()));
    GetNodeAttribute(tDiff, "delta", Delta);

    TConfigurationNode &tTurn = GetNode(t_params, "wheel_turning");
    CDegrees cAngle;
    GetNodeAttribute(tTurn, "hard_turn_angle_threshold", cAngle);
    HardTurnOnAngleThreshold = ToRadians(cAngle);
    GetNodeAttribute(tTurn, "soft_turn_angle_threshold", cAngle);
    SoftTurnOnAngleThreshold = ToRadians(cAngle);
    GetNodeAttribute(tTurn, "no_turn_angle_threshold", cAngle);
    NoTurnAngleThreshold = ToRadians(cAngle);
    GetNodeAttribute(tTurn, "max_speed", MaxSpeed);

    TConfigurationNode &tPh = GetNode(t_params, "pheromone");
    GetNodeAttribute(tPh, "a_max", AMax);
    GetNodeAttribute(tPh, "lambda_dep", LambdaDep);
    GetNodeAttribute(tPh, "theta_on", ThetaOn);
    GetNodeAttribute(tPh, "theta_off", ThetaOff);
    GetNodeAttribute(tPh, "delta_up", DeltaUp);
    GetNodeAttribute(tPh, "end_radius", EndRadius);
    PeakTicks = ToTicks(tPh, "t_peak", f_tps);
    FollowMinTicks = ToTicks(tPh, "t_follow_min", f_tps);
    RestTicks = ToTicks(tPh, "t_rest", f_tps);
    SearchTicks = ToTicks(tPh, "t_search", f_tps);
    EndTicks = ToTicks(tPh, "t_end", f_tps);
    /* D-010 arm 2: follow_enabled="false" makes theta_on infinite. */
    GetNodeAttribute(tPh, "follow_enabled", FollowEnabled);
    if (!FollowEnabled)
        ThetaOn = std::numeric_limits<Real>::infinity();

    TConfigurationNode &tNest = GetNode(t_params, "nest");
    Real fX, fY;
    GetNodeAttribute(tNest, "edge_x", NestEdgeX);
    GetNodeAttribute(tNest, "centre_x", fX);
    GetNodeAttribute(tNest, "centre_y", fY);
    NestCentre.Set(fX, fY);
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
        /* M3-01 hook: role="detractor" will select the detractor machine here. */
        std::string strRole = "honest";
        GetNodeAttributeOrDefault(t_node, "role", strRole, strRole);
        if (strRole != "honest")
            THROW_ARGOSEXCEPTION("role \"" << strRole << "\" is not implemented before M3-01");
        m_sParams.Init(t_node, CPhysicsEngine::GetInverseSimulationClockTick());
    }
    catch (CARGoSException &ex)
    {
        THROW_ARGOSEXCEPTION_NESTED("Error initializing pheromone_forager for robot \"" << GetId() << "\"", ex);
    }
    m_pcRNG = CRandom::CreateRNG("argos");
    Reset();
}

void CPheromoneForager::Reset()
{
    m_sReading = SPheromoneReading();
    m_sDeposit = SDepositRequest();
    m_sFoodData.Reset();
    m_ePeakEvent = PEAK_NONE;
    m_bFollowStart = false;
    m_eTurning = NO_TURN;
    m_unTripTicks = 0;
    m_unCarryTicks = 0;
    m_bWasCarrying = false;
    m_fHereEntry = 0.0f;
    Enter(STATE_REST);
}

/****************************************/
/****************************************/

void CPheromoneForager::ControlStep()
{
    m_ePeakEvent = PEAK_NONE;
    m_bFollowStart = false;
    m_sDeposit.active = false;
    UpdatePose();

    bool bCarrying = m_sFoodData.HasFoodItem;
    if (bCarrying && !m_bWasCarrying)
        m_unCarryTicks = 0;
    if (bCarrying)
        ++m_unCarryTicks;
    m_bWasCarrying = bCarrying;

    /* Pickup in SEARCH, FOLLOW or END_SEARCH ends the search. */
    if (bCarrying && m_eState != STATE_RETURN)
        Enter(STATE_RETURN);
    ++m_unStateTicks;
    if (m_eState == STATE_SEARCH || m_eState == STATE_FOLLOW || m_eState == STATE_END_SEARCH)
    {
        ++m_unTripTicks;
        if (m_unTripTicks > m_sParams.SearchTicks)
            Enter(STATE_RETURN);
    }

    switch (m_eState)
    {
    case STATE_REST: Rest(); break;
    case STATE_SEARCH: Search(); break;
    case STATE_FOLLOW: Follow(); break;
    case STATE_END_SEARCH: EndSearch(); break;
    case STATE_RETURN: Return(); break;
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
        if (m_sReading.probe[i] > m_sReading.probe[unBest])
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
