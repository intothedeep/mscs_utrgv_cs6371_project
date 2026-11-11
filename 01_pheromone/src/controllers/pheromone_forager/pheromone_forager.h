#ifndef PHEROMONE_FORAGER_H
#define PHEROMONE_FORAGER_H

#include <argos3/core/control_interface/ci_controller.h>
#include <argos3/core/utility/math/rng.h>
#include <argos3/core/utility/math/vector2.h>
#include <argos3/plugins/robots/generic/control_interface/ci_differential_steering_actuator.h>
#include <argos3/plugins/robots/generic/control_interface/ci_leds_actuator.h>
#include <argos3/plugins/robots/generic/control_interface/ci_positioning_sensor.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_proximity_sensor.h>

using namespace argos;

/*
 * Honest forager (DESIGN section 3.2). The loop functions play the sensor
 * hardware: they write SPheromoneReading and SFoodData before ControlStep
 * and apply SDepositRequest after it (DESIGN section 2.1). The controller
 * never sees the layer split, a deposit's creator or any robot's role.
 */
class CPheromoneForager : public CCI_Controller
{
public:
    static constexpr size_t NUM_PROBES = 8;

    /* Virtual pheromone sensor: sum of both layers, centre and 8 probe points.
       probe[0] is straight ahead, probe[k] is k * 45 degrees counter-clockwise. */
    struct SPheromoneReading
    {
        Real here;
        Real probe[NUM_PROBES];
        SPheromoneReading();
    };

    /* What the controller asks the floor to take this tick. */
    struct SDepositRequest
    {
        bool active;
        Real amount;
        SDepositRequest();
    };

    /* Same fields as hw5 SFoodData. The loop functions own the writes. */
    struct SFoodData
    {
        bool HasFoodItem;
        size_t FoodItemIdx;
        size_t TotalFoodItems;
        SFoodData();
        void Reset();
    };

    enum EState
    {
        STATE_REST = 0,
        STATE_SEARCH,
        STATE_FOLLOW,
        STATE_END_SEARCH,
        STATE_RETURN
    };

    /* Peak flag of this tick. Valid peaks may become suspects in M3. */
    enum EPeak
    {
        PEAK_NONE = 0,
        PEAK_VALID,
        PEAK_INVALID
    };

    CPheromoneForager();
    virtual ~CPheromoneForager() {}

    virtual void Init(TConfigurationNode &t_node);
    virtual void ControlStep();
    virtual void Reset();
    virtual void Destroy() {}

    inline EState GetState() const { return m_eState; }
    inline bool IsCarrying() const { return m_sFoodData.HasFoodItem; }
    /* Both flags describe the last ControlStep only (cleared at its start). */
    inline EPeak GetPeakEvent() const { return m_ePeakEvent; }
    inline bool GetFollowStart() const { return m_bFollowStart; }

    inline SFoodData &GetFoodData() { return m_sFoodData; }
    inline SPheromoneReading &GetPheromoneReading() { return m_sReading; }
    inline SDepositRequest &GetDepositRequest() { return m_sDeposit; }

private:
    struct SParams
    {
        Real MaxSpeed;
        /* Diffusion (hw5) */
        Real Delta;
        CRange<CRadians> GoStraightAngleRange;
        /* Wheel turning (hw5) */
        CRadians HardTurnOnAngleThreshold, SoftTurnOnAngleThreshold, NoTurnAngleThreshold;
        /* Pheromone (DESIGN Table 2) */
        Real AMax, LambdaDep, ThetaOn, ThetaOff, DeltaUp, EndRadius;
        bool FollowEnabled;
        UInt32 PeakTicks, FollowMinTicks, RestTicks, SearchTicks, EndTicks;
        /* Nest by position (D-008) */
        Real NestEdgeX;
        CVector2 NestCentre;
        SParams();
        void Init(TConfigurationNode &t_params, Real f_ticks_per_second);
    };

    enum ETurning { NO_TURN = 0, SOFT_TURN, HARD_TURN };

    /* States (pheromone_forager_states.cpp) */
    void Enter(EState e_state);
    void Rest();
    void Search();
    void Follow();
    void EndSearch();
    void Return();
    bool TryEnterFollow();
    void RequestDeposit();
    /* Motion (pheromone_forager.cpp) */
    void UpdatePose();
    bool IsInNest() const;
    CVector2 DiffusionVector(bool &b_collision);
    void SetWheelSpeedsFromVector(const CVector2 &c_heading);
    void Wander();
    void SteerToward(const CRadians &c_relative_angle);
    CRadians AngleTo(const CVector2 &c_point) const;
    size_t BestProbe() const;

private:
    CCI_DifferentialSteeringActuator *m_pcWheels;
    CCI_LEDsActuator *m_pcLEDs;
    CCI_PositioningSensor *m_pcPositioning;
    CCI_FootBotProximitySensor *m_pcProximity;
    CRandom::CRNG *m_pcRNG;

    SParams m_sParams;
    SPheromoneReading m_sReading;
    SDepositRequest m_sDeposit;
    SFoodData m_sFoodData;

    EState m_eState;
    EPeak m_ePeakEvent;
    bool m_bFollowStart;
    ETurning m_eTurning;

    CVector2 m_cPos;
    CRadians m_cYaw;
    CRadians m_cWanderYaw; /* absolute heading the random walk holds */

    UInt32 m_unStateTicks;  /* ticks since the last Enter() */
    UInt32 m_unTripTicks;   /* ticks since leaving REST, for t_search */
    UInt32 m_unCarryTicks;  /* ticks since pickup, for tau */
    bool m_bWasCarrying;
    UInt32 m_unFlatTicks;   /* consecutive ticks with every probe <= here */
    UInt32 m_unLowTicks;    /* consecutive ticks with every probe < theta_off */
    Real m_fHereEntry;
    CVector2 m_cPeakPos;
};

#endif
