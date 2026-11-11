#ifndef FOOD_FIELD_H
#define FOOD_FIELD_H

#include <functional>
#include <vector>

/*
 * Food sources and decoys (DESIGN section 3.1). Pure: the caller passes the
 * random draw, so this file has no simulator header. Layout stream: the loop
 * functions pass a draw from the "layout" category seeded with the run seed.
 */
namespace pheromone
{
    struct SPoint
    {
        double x;
        double y;
    };

    constexpr int NUM_SOURCES = 3;
    constexpr int NUM_DECOYS = 2;
    constexpr double SPOT_RADIUS_M = 0.25;
    constexpr double SOURCE_X_MIN = 0.5, SOURCE_X_MAX = 1.7;
    constexpr double SPOT_Y_LIMIT = 1.6;      /* keeps a disc clear of the +-1.95 m wall faces */
    constexpr double MIN_DECOY_GAP_M = 1.5;   /* decoy centre to every source centre */
    /* Decoy distance band from the nest edge point (-1, 0): the source band
       x 0.5..1.7 at y = 0 is 1.5..2.7 m from it (DESIGN Table 2, inference).
       Decoys also stay in x >= DECOY_X_MIN, outside the nest. */
    constexpr double NEST_EDGE_X = -1.0;
    constexpr double DECOY_BAND_MIN = 1.5, DECOY_BAND_MAX = 2.7;
    constexpr double DECOY_X_MIN = -0.5;

    class CFoodField
    {
    public:
        /* Uniform draw in [min, max). */
        using TUniform = std::function<double(double, double)>;

        /* Always draws 3 sources then 2 decoys, so every cell of one seed
           shares one layout (D-009). Throws std::runtime_error when no decoy
           spot meets the gap after many tries. */
        void Draw(const TUniform &f_uniform);

        /* True inside a source disc. A pickup never empties a source. */
        bool IsOnSource(double f_x, double f_y) const;

        const std::vector<SPoint> &Sources() const { return m_vecSources; }
        const std::vector<SPoint> &Decoys() const { return m_vecDecoys; }
        /* The first min(n_det, 2) decoys: d = 1, 2, 4 use 1, 2, 2 (D-009). */
        std::vector<SPoint> ActiveDecoys(unsigned n_det) const;

    private:
        std::vector<SPoint> m_vecSources;
        std::vector<SPoint> m_vecDecoys;
    };
}

#endif
