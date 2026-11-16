#ifndef IS_SPIRAL_PATH_H
#define IS_SPIRAL_PATH_H

// Square spiral for search_mode = spiral or hybrid (DESIGN 3.6 T4 form, D-025). PURE: no ARGoS include.
// From the centre, legs go east, north, west, south, east, ... with lengths g, g, 2g, 2g, 3g, 3g, ...
// A point on the path is named by its path length s from the centre.

#include <cmath>
#include <cstddef>

#include "visit_map.h"

namespace InformedSearch {

struct SpiralPath {
    Point centre;
    double gap; // g

    // Length of leg index i: g * (i / 2 + 1).
    double LegLength(std::size_t i) const { return gap * static_cast<double>(i / 2 + 1); }

    // Path length at the end of leg index i.
    double LegEnd(std::size_t i) const {
        double total = 0.0;
        for (std::size_t j = 0; j <= i; ++j) total += LegLength(j);
        return total;
    }

    // Point at path length s (s >= 0). Writes the index of the leg holding it to *leg.
    Point At(double s, std::size_t* leg) const {
        static const int dx[4] = {1, 0, -1, 0};
        static const int dy[4] = {0, 1, 0, -1};
        Point p = centre;
        double remaining = s;
        std::size_t i = 0;
        while (remaining > LegLength(i)) {
            p.x += dx[i % 4] * LegLength(i);
            p.y += dy[i % 4] * LegLength(i);
            remaining -= LegLength(i);
            ++i;
        }
        p.x += dx[i % 4] * remaining;
        p.y += dy[i % 4] * remaining;
        *leg = i;
        return p;
    }

    // Half-side of the square through p (Chebyshev distance from the centre).
    double HalfSide(const Point& p) const {
        const double ax = std::fabs(p.x - centre.x);
        const double ay = std::fabs(p.y - centre.y);
        return ax > ay ? ax : ay;
    }
};

} // namespace InformedSearch

#endif
