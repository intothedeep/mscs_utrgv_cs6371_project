#include "pheromone_forager.h"

/*
 * Defense rule, DESIGN section 3.4. No communication: the suspect list is private.
 * Rule 1 (record a valid peak) is in EndSearch(), rule 5 (cone abort) in Follow().
 * Every function here does nothing when the defense param is off.
 */

/* Rules 2 and 3: merge into a point within r_merge, else append; drop the oldest. */
void CPheromoneForager::AddSuspect(const CVector2 &c_point)
{
    for (SSuspect &sSuspect : m_vecSuspects)
    {
        if ((sSuspect.Pos - c_point).Length() <= m_sParams.RMerge)
        {
            const Real fCount = static_cast<Real>(sSuspect.Count);
            sSuspect.Pos = (sSuspect.Pos * fCount + c_point) * (1.0f / (fCount + 1.0f));
            ++sSuspect.Count;
            return;
        }
    }
    m_vecSuspects.push_back({c_point, 1});
    if (m_vecSuspects.size() > m_sParams.NMem)
        m_vecSuspects.erase(m_vecSuspects.begin());
}

/* v5: a point acts (mask, cone) once it holds Count >= confirm_k failures. confirm_k 1 = v4. */
bool CPheromoneForager::IsActive(const SSuspect &s_suspect) const
{
    return s_suspect.Count >= m_sParams.ConfirmK;
}

/* Rule 4: a reading taken within r_suspect of a suspect point is read as 0. */
void CPheromoneForager::MaskSuspects()
{
    m_sSeen = m_sReading;
    if (!m_sParams.DefenseEnabled || m_vecSuspects.empty())
        return;
    auto cIsSuspect = [this](const CVector2 &c_point)
    {
        for (const SSuspect &sSuspect : m_vecSuspects)
            if (IsActive(sSuspect) && (sSuspect.Pos - c_point).Length() <= m_sParams.RSuspect)
                return true;
        return false;
    };
    if (cIsSuspect(m_cPos))
        m_sSeen.here = 0.0f;
    for (size_t i = 0; i < NUM_PROBES; ++i)
    {
        CRadians cAngle = m_cYaw + CRadians::PI_OVER_FOUR * static_cast<Real>(i);
        if (cIsSuspect(m_cPos + CVector2(m_sParams.ProbeRadius, cAngle)))
            m_sSeen.probe[i] = 0.0f;
    }
}

/* Rule 5 test: a suspect within +-alpha_cone of the heading and within d_cone. */
bool CPheromoneForager::IsConeHit() const
{
    if (!m_sParams.DefenseEnabled)
        return false;
    for (const SSuspect &sSuspect : m_vecSuspects)
    {
        if (!IsActive(sSuspect))
            continue;
        const CVector2 cToSuspect = sSuspect.Pos - m_cPos;
        if (cToSuspect.Length() <= m_sParams.DCone &&
            Abs((cToSuspect.Angle() - m_cYaw).SignedNormalize()) <= m_sParams.AlphaCone)
            return true;
    }
    return false;
}
