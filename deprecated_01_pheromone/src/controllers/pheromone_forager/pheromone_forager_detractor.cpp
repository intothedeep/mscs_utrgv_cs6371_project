#include "pheromone_forager.h"

/*
 * Detractor, DESIGN section 3.3: REST, GO_DECOY, WAIT_DECOY (2 s, mimics a pickup),
 * RETURN_LAY, repeat. It never carries food. It lays the honest deposit profile,
 * into the false layer (the loop functions choose the layer by the hb_ / dt_ prefix).
 */

void CPheromoneForager::GoDecoy()
{
    if ((m_cDecoy - m_cPos).Length() <= m_sParams.DecoyReach)
    {
        m_bDecoyReach = true;
        Enter(STATE_WAIT_DECOY);
        return;
    }
    SteerToward(AngleTo(m_cDecoy));
}

void CPheromoneForager::WaitDecoy()
{
    m_pcWheels->SetLinearVelocity(0.0f, 0.0f);
    if (m_unStateTicks >= m_sParams.WaitTicks)
        Enter(STATE_RETURN_LAY); /* tau restarts at 0 on the next step (ControlStep) */
}

void CPheromoneForager::ReturnLay()
{
    if (IsInNest())
    {
        Enter(STATE_REST);
        return;
    }
    SteerToward(AngleTo(m_sParams.NestCentre));
}
