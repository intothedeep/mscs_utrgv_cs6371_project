#ifndef RUN_LOGGER_H
#define RUN_LOGGER_H

#include "food_field.h"
#include <fstream>
#include <string>
#include <utility>
#include <vector>

/*
 * Writes one run folder: manifest.json, ticks.csv, robots.csv, events.csv
 * (DESIGN section 4, schema_version 1). Pure: no simulator header.
 * Every Log call is a no-op until Open() succeeds, so a Qt demo run with no
 * <logger> node writes nothing and needs no checks at the call sites.
 */
namespace pheromone
{
    constexpr int NUM_STATES = 5; /* REST, SEARCH, FOLLOW, END_SEARCH, RETURN */

    struct STick
    {
        unsigned tick;
        unsigned food;
        double wastedSeconds;
        unsigned states[NUM_STATES]; /* honest robots per state, ticks.csv n_* order */
        double pherTrue;
        double pherFalse;
        unsigned suspects;
    };

    struct SRunInfo
    {
        std::string root;   /* the run folder is <root>/<runid>/ */
        std::string runid;
        std::string codeVersion;
        std::string shaLoopFunctions, shaController, gitCommit;
        bool gitDirty = false;
        /* The four params that check_runs.py reads as numbers ... */
        long nDet = 0, defense = 0, seed = 0;
        double lengthSeconds = 0.0;
        /* ... and every other .argos value, written as a string. */
        std::vector<std::pair<std::string, std::string>> otherParams;
        std::vector<SPoint> sources, decoys;
        unsigned decoysUsed = 0;
        double radius = 0.0;
        std::string machine, argos;
        int threads = 0;
        unsigned expectedTicks = 0;
    };

    class CRunLogger
    {
    public:
        /* Creates the run folder and the three CSV files. Throws std::runtime_error. */
        void Open(const SRunInfo &s_info);
        bool IsOpen() const { return m_bOpen; }

        void LogTick(const STick &s_tick);
        void LogRobot(unsigned un_tick, const std::string &str_id, const std::string &str_role,
                      double f_x, double f_y, double f_yaw_deg, const std::string &str_state,
                      int n_carrying, double f_here, double f_false_share);
        void LogEvent(unsigned un_tick, const std::string &str_id, const std::string &str_event,
                      double f_x, double f_y);
        /* Writes manifest.json from the last tick row. Safe to call twice. */
        void Close();

    private:
        bool m_bOpen = false;
        SRunInfo m_sInfo;
        STick m_sLast{};
        unsigned m_unRows = 0;
        std::ofstream m_cTicks, m_cRobots, m_cEvents;
    };

    /* One formatter for the CSV cell and the manifest metric, so they match. */
    std::string FormatNumber(double f_value);
}

#endif
