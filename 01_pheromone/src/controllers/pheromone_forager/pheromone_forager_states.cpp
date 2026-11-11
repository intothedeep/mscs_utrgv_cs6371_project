#include "pheromone_forager.h"
#include <argos3/core/simulator/physics_engine/physics_engine.h>
#include <algorithm>
#include <cmath>

/*
 * Honest state machine, DESIGN section 3.2 (Figure 2 and Table 2a).
 * Each state method runs once per ControlStep and may call Enter().
 * Detractor states are in pheromone_forager_detractor.cpp, the defense in
 * pheromone_forager_defense.cpp.
 */

/****************************************/
/****************************************/

void CPheromoneForager::Enter(EState e_state)
{
    m_eState = e_state;
    m_unStateTicks = 0;
    /* DESIGN Table 2a: a detractor is red in every state. No controller senses LEDs,
       so the colour does not reveal the role to an honest robot. */
    if (m_bDetractor)
    {
        m_pcLEDs->SetAllColors(CColor::RED);
        return;
    }
    switch (e_state)
    {
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
        m_pcLEDs->SetAllColors(CColor::MAGENTA);
        m_cWanderYaw = m_cYaw;
        break;
    case STATE_RETURN:
        m_pcLEDs->SetAllColors(CColor::BLUE);
        break;
    default: /* STATE_REST: off */
        m_pcLEDs->SetAllColors(CColor::BLACK);
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
        Enter(m_bDetractor ? STATE_GO_DECOY : STATE_SEARCH);
    }
}

/* FOLLOW entry: the largest probe beats theta_on and beats here + delta_up.
   A flat ridge therefore never starts a follow. With the defense on, a suspect
   point ahead in the cone blocks the entry: the abort would fire at once.
   v4: for t_lock after a cone abort the entry is closed. Follow() turns the robot 90 degrees,
   so without the lock the cone is empty and the robot re-enters 0.6 s later. */
bool CPheromoneForager::TryEnterFollow()
{
    if (m_unLockLeft > 0)
        return false;
    Real fBest = m_sSeen.probe[BestProbe()];
    if (fBest > m_sParams.ThetaOn && fBest > m_sSeen.here + m_sParams.DeltaUp && !IsConeHit())
    {
        m_fHereEntry = m_sSeen.here;
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
    /* Rule 5: a suspect point ahead in the cone aborts the follow. Turn 90 degrees
       away, or the robot walks on toward the false end it just refused. */
    if (IsConeHit())
    {
        m_bConeAbort = true;
        m_unLockLeft = m_sParams.LockTicks;
        Enter(STATE_SEARCH);
        const Real fSide = m_pcRNG->Bernoulli(0.5f) ? 1.0f : -1.0f;
        m_cWanderYaw = (m_cYaw + CRadians::PI_OVER_TWO * fSide).SignedNormalize();
        return;
    }
    Real fBest = m_sSeen.probe[BestProbe()];
    m_unLowTicks = (fBest < m_sParams.ThetaOff) ? m_unLowTicks + 1 : 0;
    m_unFlatTicks = (fBest <= m_sSeen.here) ? m_unFlatTicks + 1 : 0;

    /* Trail lost by a low reading: back to SEARCH, no peak, no suspect. */
    if (m_unLowTicks >= m_sParams.PeakTicks)
    {
        Enter(STATE_SEARCH);
        return;
    }
    /* Peak: valid or invalid, both search around it (END_SEARCH). Only a
       valid peak may add a suspect. */
    if (m_unFlatTicks >= m_sParams.PeakTicks)
    {
        m_bPeakValid = m_unStateTicks >= m_sParams.FollowMinTicks &&
                       m_sSeen.here >= 2.0f * std::max(m_fHereEntry, m_sParams.ThetaOn);
        m_ePeakEvent = m_bPeakValid ? PEAK_VALID : PEAK_INVALID;
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
        /* Rule 1: a valid peak with no food becomes a suspect point. Pickup would
           have moved the robot to RETURN already, so no food is certain here. */
        if (m_sParams.DefenseEnabled && m_bPeakValid)
        {
            AddSuspect(m_cPeakPos);
            m_bSuspectAdd = true;
        }
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

/* amount = A_max * exp(-lambda_dep * tau): strongest at the food (or the decoy), so
   uphill points to it (DESIGN section 3.2). Never inside the nest. */
void CPheromoneForager::RequestDeposit()
{
    const bool bLaying = m_sFoodData.HasFoodItem || m_eState == STATE_RETURN_LAY;
    if (!bLaying || IsInNest())
        return;
    Real fTau = static_cast<Real>(m_unTauTicks) * CPhysicsEngine::GetSimulationClockTick();
    m_sDeposit.active = true;
    m_sDeposit.amount = m_sParams.AMax * std::exp(-m_sParams.LambdaDep * fTau);
}
