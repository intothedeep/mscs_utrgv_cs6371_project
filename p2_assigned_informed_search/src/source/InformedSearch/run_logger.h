#ifndef IS_RUN_LOGGER_H
#define IS_RUN_LOGGER_H

// Run logs of DESIGN 5.1: queries.csv and points.csv in the working directory of the run.
// Writes files only. It never draws a random number and never writes state a controller
// reads (DESIGN 4.1). The column lists and the tag below must equal tools/schema.py
// (QUERIES_COLUMNS, POINTS_COLUMNS, METRICS_TAG).

#include <fstream>
#include <iomanip>
#include <string>

namespace InformedSearch {

// Prefix of the one stdout line printed at run end (schema.METRICS_TAG).
constexpr const char* kMetricsTag = "IS_METRICS";

class RunLogger {
public:
    // Truncate both files and write their headers. Call once, at Init.
    void Open() {
        queries_.open("queries.csv", std::ios::trunc);
        queries_ << "t_s,robot,branch,nodes_visited,nodes_total,leaves_total,points_inserted_total,"
                    "query_us,target_x,target_y,dist_m,reached\n";
        points_.open("points.csv", std::ios::trunc);
        points_ << "t_s,robot,x,y,kind\n";
        Flush();
    }

    // One row per decision. Cost and target columns stay empty here (they are filled by the
    // map query path, M3-06).
    void LogQuery(double t_s, const std::string& robot, const std::string& branch) {
        queries_ << std::fixed << std::setprecision(3) << t_s << ',' << robot << ',' << branch
                 << ",,,,,,,,,\n"; // 9 empty columns after branch
        queries_.flush();
    }

    // One row per point. kind is "pickup" (logged at the pickup, every arm that runs our build)
    // or "visit" (logged at upload time, switch on only; the replay reads these, D-026).
    void LogPoint(double t_s, const std::string& robot, double x, double y, const char* kind) {
        points_ << std::fixed << std::setprecision(3) << t_s << ',' << robot << ',' << x << ',' << y << ','
                << kind << '\n';
    }

    void Flush() {
        queries_.flush();
        points_.flush();
    }

private:
    std::ofstream queries_;
    std::ofstream points_;
};

} // namespace InformedSearch

#endif
