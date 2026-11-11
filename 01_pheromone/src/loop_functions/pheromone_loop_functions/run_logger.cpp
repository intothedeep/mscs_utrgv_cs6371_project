#include "run_logger.h"
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <stdexcept>

namespace pheromone
{
    /* Headers are in schema.py order (tools/schema.py TICKS_COLUMNS, ROBOTS_COLUMNS,
       EVENTS_COLUMNS). check_runs.py rejects any difference. */
    static const char *TICKS_HEADER = "tick,food_collected,wasted_robot_seconds,n_rest,n_search,"
                                      "n_follow,n_end,n_return,pher_true_sum,pher_false_sum,"
                                      "suspects_total,mock";
    static const char *ROBOTS_HEADER = "tick,robot_id,role,x,y,yaw_deg,state,carrying,here,false_share";
    static const char *EVENTS_HEADER = "tick,robot_id,event,x,y";

    std::string FormatNumber(double f_value)
    {
        std::ostringstream cOut;
        cOut << std::setprecision(10) << f_value;
        return cOut.str();
    }

    static std::string Quote(const std::string &str)
    {
        std::string strOut = "\"";
        for (char c : str)
        {
            if (c == '"' || c == '\\')
                strOut += '\\';
            strOut += c;
        }
        return strOut + "\"";
    }

    static std::string Points(const std::vector<SPoint> &vec_points)
    {
        std::string strOut = "[";
        for (size_t i = 0; i < vec_points.size(); ++i)
            strOut += std::string(i ? ", " : "") + "[" + FormatNumber(vec_points[i].x) + ", " +
                      FormatNumber(vec_points[i].y) + "]";
        return strOut + "]";
    }

    static void OpenFile(std::ofstream &c_file, const std::string &str_path, const char *pch_header)
    {
        c_file.open(str_path, std::ios_base::trunc | std::ios_base::out);
        if (!c_file)
            throw std::runtime_error("run_logger: cannot open " + str_path);
        c_file << pch_header << "\n";
    }

    void CRunLogger::Open(const SRunInfo &s_info)
    {
        m_sInfo = s_info;
        const std::string strFolder = s_info.root + "/" + s_info.runid;
        std::filesystem::create_directories(strFolder);
        OpenFile(m_cTicks, strFolder + "/ticks.csv", TICKS_HEADER);
        OpenFile(m_cRobots, strFolder + "/robots.csv", ROBOTS_HEADER);
        OpenFile(m_cEvents, strFolder + "/events.csv", EVENTS_HEADER);
        m_bOpen = true;
    }

    void CRunLogger::LogTick(const STick &s_tick)
    {
        if (!m_bOpen)
            return;
        m_cTicks << s_tick.tick << "," << s_tick.food << "," << FormatNumber(s_tick.wastedSeconds);
        for (unsigned unCount : s_tick.states)
            m_cTicks << "," << unCount;
        /* mock = 0: a real run (the manifest says false). */
        m_cTicks << "," << FormatNumber(s_tick.pherTrue) << "," << FormatNumber(s_tick.pherFalse)
                 << "," << s_tick.suspects << ",0\n";
        m_sLast = s_tick;
        ++m_unRows;
    }

    void CRunLogger::LogRobot(unsigned un_tick, const std::string &str_id, const std::string &str_role,
                              double f_x, double f_y, double f_yaw_deg, const std::string &str_state,
                              int n_carrying, double f_here, double f_false_share)
    {
        if (!m_bOpen)
            return;
        m_cRobots << un_tick << "," << str_id << "," << str_role << "," << FormatNumber(f_x) << ","
                  << FormatNumber(f_y) << "," << FormatNumber(f_yaw_deg) << "," << str_state << ","
                  << n_carrying << "," << FormatNumber(f_here) << "," << FormatNumber(f_false_share) << "\n";
    }

    void CRunLogger::LogEvent(unsigned un_tick, const std::string &str_id, const std::string &str_event,
                              double f_x, double f_y)
    {
        if (!m_bOpen)
            return;
        m_cEvents << un_tick << "," << str_id << "," << str_event << "," << FormatNumber(f_x) << ","
                  << FormatNumber(f_y) << "\n";
    }

    void CRunLogger::Close()
    {
        if (!m_bOpen)
            return;
        m_bOpen = false; /* a second call (PostExperiment then Destroy) does nothing */
        m_cTicks.close();
        m_cRobots.close();
        m_cEvents.close();
        const SRunInfo &i = m_sInfo;
        std::ofstream cOut(i.root + "/" + i.runid + "/manifest.json", std::ios_base::trunc);
        cOut << "{\n  \"schema_version\": 1, \"mock\": false,\n"
             << "  \"runid\": " << Quote(i.runid) << ",\n"
             << "  \"code_version\": " << Quote(i.codeVersion) << ",\n"
             << "  \"code_sha\": {\"loop_functions\": " << Quote(i.shaLoopFunctions)
             << ", \"controller\": " << Quote(i.shaController) << "},\n"
             << "  \"git_commit\": " << Quote(i.gitCommit) << ", \"git_dirty\": "
             << (i.gitDirty ? "true" : "false") << ",\n"
             << "  \"params\": {\"n_det\": " << i.nDet << ", \"defense\": " << i.defense
             << ", \"seed\": " << i.seed << ", \"length_s\": " << FormatNumber(i.lengthSeconds);
        for (const auto &cParam : i.otherParams)
            cOut << ", " << Quote(cParam.first) << ": " << Quote(cParam.second);
        cOut << "},\n"
             << "  \"layout\": {\"layout_seed\": " << i.seed << ", \"sources\": " << Points(i.sources)
             << ", \"decoys\": " << Points(i.decoys) << ", \"n_decoys_used\": " << i.decoysUsed
             << ", \"radius_m\": " << FormatNumber(i.radius) << "},\n"
             << "  \"env\": {\"machine\": " << Quote(i.machine) << ", \"argos\": " << Quote(i.argos)
             << ", \"threads\": " << i.threads << "},\n"
             << "  \"metrics\": {\"food_collected\": " << m_sLast.food
             << ", \"wasted_robot_seconds\": " << FormatNumber(m_sLast.wastedSeconds)
             << ", \"ticks\": " << m_unRows << ", \"complete\": "
             << (m_unRows == i.expectedTicks ? "true" : "false") << "}\n}\n";
    }
}
