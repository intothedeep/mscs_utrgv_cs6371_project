#include "pheromone_forager.h"
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <cmath>

/*
 * Honest state machine, DESIGN section 3.2 (Figure 2 and Table 2a).
 * Each state method runs once per ControlStep and may call Enter().
 */

/****************************************/
/****************************************/

void CPheromoneForager::Enter(EState e_state)
{
    m_eState = e_state;
    m_unStateTicks = 0;
    switch (e_state)
    {
    case STATE_REST:
        m_pcLEDs->SetAllColors(CColor::BLACK);
        break;
    case STATE_SEARCH:
        m_pcLEDs->SetAllColors(CColor::GREEN);
        m_cWanderYaw = m_cYaw;
        break;
    case STATE_FOLLOW:
        m_pcLEDs->SetAllColors(CColor::YELLOW);
        m_unFlatTicks = 0;
        m_unLowTicks = 0;
        break;
    case STATE_END_SEARCH:
        /* DESIGN Table 2a gives magenta; the display only. */
        m_pcLEDs->SetAllColors(CColor::MAGENTA);
        m_cWanderYaw = m_cYaw;
        break;
    case STATE_RETURN:
        m_pcLEDs->SetAllColors(CColor::BLUE);
        break;
    }
}

/****************************************/
/****************************************/

void CPheromoneForager::Rest()
{
    m_pcWheels->SetLinearVelocity(0.0f, 0.0f);
    if (m_unStateTicks >= m_sParams.RestTicks)
    {
        m_unTripTicks = 0;
        Enter(STATE_SEARCH);
    }
}

/* FOLLOW entry: the largest probe beats theta_on and beats here + delta_up.
   A flat ridge therefore never starts a follow. */
bool CPheromoneForager::TryEnterFollow()
{
    Real fBest = m_sReading.probe[BestProbe()];
    if (fBest > m_sParams.ThetaOn && fBest > m_sReading.here + m_sParams.DeltaUp)
    {
        m_fHereEntry = m_sReading.here;
        m_bFollowStart = true;
        Enter(STATE_FOLLOW);
        return true;
    }
    return false;
}

void CPheromoneForager::Search()
{
    if (TryEnterFollow())
        return;
    Wander();
}

void CPheromoneForager::Follow()
{
    Real fBest = m_sReading.probe[BestProbe()];
    m_unLowTicks = (fBest < m_sParams.ThetaOff) ? m_unLowTicks + 1 : 0;
    m_unFlatTicks = (fBest <= m_sReading.here) ? m_unFlatTicks + 1 : 0;

    /* Trail lost by a low reading: back to SEARCH, no peak, no suspect. */
    if (m_unLowTicks >= m_sParams.PeakTicks)
    {
        Enter(STATE_SEARCH);
        return;
    }
    /* Peak: valid or invalid, both search around it (END_SEARCH). Only a
       valid peak may add a suspect in M3-02. */
    if (m_unFlatTicks >= m_sParams.PeakTicks)
    {
        bool bValid = m_unStateTicks >= m_sParams.FollowMinTicks &&
                      m_sReading.here >= 2.0f * m_fHereEntry;
        m_ePeakEvent = bValid ? PEAK_VALID : PEAK_INVALID;
        m_cPeakPos = m_cPos;
        Enter(STATE_END_SEARCH);
        return;
    }
    /* Probe k lies k * 45 degrees counter-clockwise of the heading. */
    SteerToward((CRadians::PI_OVER_FOUR * static_cast<Real>(BestProbe())).SignedNormalize());
}

void CPheromoneForager::EndSearch()
{
    if (m_unStateTicks >= m_sParams.EndTicks)
    {
        /* M3-02 hook: a valid peak with no food becomes a suspect point here,
           when the defense parameter is 1. M2 never adds one. */
        Enter(STATE_SEARCH);
        return;
    }
    if ((m_cPeakPos - m_cPos).Length() > m_sParams.EndRadius)
        SteerToward(AngleTo(m_cPeakPos));
    else
        Wander();
}

void CPheromoneForager::Return()
{
    if (!m_sFoodData.HasFoodItem && IsInNest())
    {
        Enter(STATE_REST);
        return;
    }
    SteerToward(AngleTo(m_sParams.NestCentre));
}

/* amount = A_max * exp(-lambda_dep * tau): strongest at the food, so uphill
   points to the food (DESIGN section 3.2). Never inside the nest. */
void CPheromoneForager::RequestDeposit()
{
    if (!m_sFoodData.HasFoodItem || IsInNest())
        return;
    Real fTau = static_cast<Real>(m_unCarryTicks) * CPhysicsEngine::GetSimulationClockTick();
    m_sDeposit.active = true;
    m_sDeposit.amount = m_sParams.AMax * std::exp(-m_sParams.LambdaDep * fTau);
}
