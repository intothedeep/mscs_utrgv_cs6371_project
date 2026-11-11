#ifndef DEFENSE_LOG_H
#define DEFENSE_LOG_H

#include <fstream>
#include <string>

/*
 * Sidecar defense_log.csv of the ID arm (DESIGN_M6 section 5, Table 4). One row per event per
 * affected robot. Pure: no simulator header. Write() is a no-op until Open() succeeds, so a run
 * with no <logger> writes nothing. schema.py and the four schema files stay as they are.
 */
namespace pheromone
{
    struct SDefenseRow
    {
        unsigned tick;
        std::string robotId, role, event;
        int checkId, strikes, isolated, groupSize;
        std::string trailCreator;
        int deadlineTick;
        std::string groupSource;
        int cellsZeroed;
        double x, y;
    };

    class CDefenseLog
    {
    public:
        /* Creates the file and writes the header row, so a run with no event still has the file. */
        void Open(const std::string &str_path);
        bool IsOpen() const { return m_cFile.is_open(); }
        void Write(const SDefenseRow &s_row);
        void Close();

    private:
        std::ofstream m_cFile;
    };
}

#endif
