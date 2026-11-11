#ifndef PHEROMONE_GRID_H
#define PHEROMONE_GRID_H

#include <array>
#include <cstddef>

/*
 * Two-layer pheromone grid (DESIGN section 2). Pure: no simulator header,
 * so it can be checked by deliberate breakage alone. Units are metres and
 * ticks. The arena inner faces are at +-2 m (DESIGN Table 2).
 */
namespace pheromone
{
    constexpr int GRID_SIZE = 40;      /* 40 x 40 cells */
    constexpr double CELL_M = 0.10;    /* whole pixels per cell at 50 px/m */
    constexpr double ARENA_MIN = -2.0; /* corner of cell (0, 0) */

    enum ELayer
    {
        LAYER_TRUE = 0,  /* laid by honest robots (hb_) */
        LAYER_FALSE = 1, /* laid by detractors (dt_) */
        NUM_LAYERS = 2
    };

    class CPheromoneGrid
    {
    public:
        /* Per-tick factor so the value halves every f_half_life_s seconds. */
        static double EvaporationFactor(double f_half_life_s, double f_ticks_per_second);

        explicit CPheromoneGrid(double f_evaporation_factor);

        void Clear();
        /* Multiply every cell by the evaporation factor. */
        void Evaporate();
        /* Write the 3 x 3 cells around (x, y). Each cell takes the max of
           its value and f_amount, so a busy trail does not build up. */
        void Deposit(ELayer e_layer, double f_x, double f_y, double f_amount);
        /* Sum of both layers in the cell holding (x, y). 0 outside the arena. */
        double Probe(double f_x, double f_y) const;
        /* One layer in that cell, for floor paint and ground truth. */
        double Value(ELayer e_layer, double f_x, double f_y) const;
        double LayerSum(ELayer e_layer) const;

    private:
        /* Cell index, or -1 when the point is outside the grid. */
        static int CellOf(double f_coordinate);

        double m_fEvaporationFactor;
        std::array<std::array<double, GRID_SIZE * GRID_SIZE>, NUM_LAYERS> m_aLayers;
    };
}

#endif
