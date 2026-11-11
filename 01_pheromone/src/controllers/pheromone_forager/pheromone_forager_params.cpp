#include "pheromone_forager.h"
#include <argos3/core/utility/configuration/argos_configuration.h>
#include <limits>

/* Every Table 2 value is read here from <params>, none is hard-coded (M2-04). */

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
    /* Must equal the loop functions' probe_radius_m: the robot knows its own antenna ring. */
    GetNodeAttribute(tPh, "probe_radius_m", ProbeRadius);
    GetNodeAttribute(tPh, "decoy_reach_m", DecoyReach);
    PeakTicks = ToTicks(tPh, "t_peak", f_tps);
    FollowMinTicks = ToTicks(tPh, "t_follow_min", f_tps);
    RestTicks = ToTicks(tPh, "t_rest", f_tps);
    SearchTicks = ToTicks(tPh, "t_search", f_tps);
    EndTicks = ToTicks(tPh, "t_end", f_tps);
    WaitTicks = ToTicks(tPh, "t_wait", f_tps);
    /* D-010 arm 2: follow_enabled="false" makes theta_on infinite. */
    GetNodeAttribute(tPh, "follow_enabled", FollowEnabled);
    if (!FollowEnabled)
        ThetaOn = std::numeric_limits<Real>::infinity();

    /* Defense rule, DESIGN section 3.4. enabled="false": rules 1 to 5 never run. */
    TConfigurationNode &tDef = GetNode(t_params, "defense");
    GetNodeAttribute(tDef, "enabled", DefenseEnabled);
    GetNodeAttribute(tDef, "r_merge", RMerge);
    GetNodeAttribute(tDef, "n_mem", NMem);
    GetNodeAttribute(tDef, "r_suspect", RSuspect);
    GetNodeAttribute(tDef, "alpha_cone_deg", cAngle);
    AlphaCone = ToRadians(cAngle);
    GetNodeAttribute(tDef, "d_cone", DCone);
    /* v4 lockout (D-028). Optional, so a v3 file without it still loads. 0 = v3 behaviour. */
    Real fLockSeconds = 0.0f;
    GetNodeAttributeOrDefault(tDef, "t_lock", fLockSeconds, fLockSeconds);
    LockTicks = static_cast<UInt32>(fLockSeconds * f_tps + 0.5f);
    /* v5 confirm-twice (D-039). Optional, so a v4 file without it still loads. 1 = v4 behaviour. */
    ConfirmK = 1;
    GetNodeAttributeOrDefault(tDef, "confirm_k", ConfirmK, ConfirmK);
    if (ConfirmK < 1)
        THROW_ARGOSEXCEPTION("defense confirm_k must be at least 1");

    TConfigurationNode &tNest = GetNode(t_params, "nest");
    Real fX, fY;
    GetNodeAttribute(tNest, "edge_x", NestEdgeX);
    GetNodeAttribute(tNest, "centre_x", fX);
    GetNodeAttribute(tNest, "centre_y", fY);
    NestCentre.Set(fX, fY);
}
