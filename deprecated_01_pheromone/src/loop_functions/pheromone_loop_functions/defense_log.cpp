#include "defense_log.h"
#include "run_logger.h"
#include <stdexcept>

namespace pheromone
{
    void CDefenseLog::Open(const std::string &str_path)
    {
        m_cFile.open(str_path);
        if (!m_cFile)
            throw std::runtime_error("cannot open " + str_path);
        m_cFile << "tick,robot_id,role,event,check_id,strikes,isolated,group_size,trail_creator,"
                   "deadline_tick,group_source,cells_zeroed,x,y\n";
    }

    void CDefenseLog::Write(const SDefenseRow &s_row)
    {
        if (!IsOpen())
            return;
        m_cFile << s_row.tick << ',' << s_row.robotId << ',' << s_row.role << ',' << s_row.event << ','
                << s_row.checkId << ',' << s_row.strikes << ',' << s_row.isolated << ',' << s_row.groupSize << ','
                << s_row.trailCreator << ',' << s_row.deadlineTick << ',' << s_row.groupSource << ','
                << s_row.cellsZeroed << ',' << FormatNumber(s_row.x) << ',' << FormatNumber(s_row.y) << '\n';
    }

    void CDefenseLog::Close()
    {
        if (m_cFile.is_open())
            m_cFile.close();
    }
}
