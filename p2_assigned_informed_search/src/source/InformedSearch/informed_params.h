#ifndef IS_INFORMED_PARAMS_H
#define IS_INFORMED_PARAMS_H

// Method parameters of DESIGN Table 6, read from the <CPFA> node of the experiment file.
// Every attribute has a default, so one experiment file runs on the vendor build (it ignores
// the unknown attributes, DESIGN 4.1 and 10) and on ours.
// Add a flag: add one field with its start value, and one ReadParam line in Read().
// The master switch InformedSearch is read by the loop functions, not here.

#include <argos3/core/utility/configuration/argos_configuration.h>
#include <limits>
#include <string>

namespace InformedSearch {

enum SearchMode { kWalk = 0, kSpiral = 1, kHybrid = 2 };

struct InformedParams {
    double cell_size = 0.3125;  // MapCellSize: minimum cell s_min (m), fixed
    double rec_period = 2.0;    // RecPeriod: seconds between logged points, fixed
    double t_stale = std::numeric_limits<double>::infinity(); // TStale (s). Attribute <= 0 = never stale
    double r_res = 1.0;         // RRes: reservation radius (m)
    double t_res = 60.0;        // TRes: reservation time (s)
    double q_map = 0.0;         // QMap: P(map target before pheromone) for a robot without fidelity
    int map_grid = 0;           // MapGrid: 1 = option A fine grid, 0 = option B quadtree (R6 fallback)
    double r_halo = 0.0;        // RHalo: T5 food halo radius (m), 0 = off (D-024)
    SearchMode search_mode = kWalk; // SearchMode: walk, spiral or hybrid (D-025)
    double spiral_gap = 0.18;   // SpiralGap: leg unit g (m), fixed (D-025)
    double crowd_window = 1.0;  // CrowdWindow: seconds that merge collision flags into one event, fixed
    int crowd_events = 2;       // CrowdEvents: c_crowd, events that end a hybrid spiral, fixed

    void Read(argos::TConfigurationNode& node) {
        ReadParam(node, "MapCellSize", cell_size);
        ReadParam(node, "RecPeriod", rec_period);
        double t_stale_attr = 0.0;
        ReadParam(node, "TStale", t_stale_attr);
        // XML cannot hold infinity for an istream read, so 0 stands for "forever".
        t_stale = t_stale_attr > 0.0 ? t_stale_attr : std::numeric_limits<double>::infinity();
        ReadParam(node, "RRes", r_res);
        ReadParam(node, "TRes", t_res);
        ReadParam(node, "QMap", q_map);
        ReadParam(node, "MapGrid", map_grid);
        ReadParam(node, "RHalo", r_halo);
        std::string mode = "walk";
        ReadParam(node, "SearchMode", mode);
        if (mode == "walk") search_mode = kWalk;
        else if (mode == "spiral") search_mode = kSpiral;
        else if (mode == "hybrid") search_mode = kHybrid;
        else THROW_ARGOSEXCEPTION("SearchMode must be walk, spiral or hybrid, got \"" << mode << "\"");
        ReadParam(node, "SpiralGap", spiral_gap);
        ReadParam(node, "CrowdWindow", crowd_window);
        ReadParam(node, "CrowdEvents", crowd_events);
    }

private:
    // The field's own start value is the default.
    template <typename T>
    static void ReadParam(argos::TConfigurationNode& node, const char* name, T& field) {
        const T start = field;
        argos::GetNodeAttributeOrDefault(node, name, field, start);
    }
};

} // namespace InformedSearch

#endif
