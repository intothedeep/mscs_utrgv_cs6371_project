#ifndef OWNER_GRID_H
#define OWNER_GRID_H

#include "pheromone_grid.h"
#include <array>
#include <utility>
#include <vector>

/*
 * Who set each cell's current value (DESIGN_M6 section 2, Table 2). One integer robot
 * index per cell and layer, -1 = none. Pure: no simulator header. An index is opaque here:
 * it never tells the role of the robot.
 */
namespace pheromone
{
    class COwnerGrid
    {
    public:
        using TCell = std::pair<int, int>; /* (layer, cell index) */

        COwnerGrid();
        void Clear();
        void SetOwner(ELayer e_layer, int n_cell, int n_robot);
        int Owner(ELayer e_layer, int n_cell) const;
        /* The owner of the larger layer value in a cell. A tie goes to the true layer.
           -1 when both values are 0. The value is physical, the layer label is storage. */
        int Dominant(int n_cell, double f_true, double f_false) const;
        /* The cells this robot still owns, now set to -1. The caller zeroes them in the grid. */
        std::vector<TCell> ReleaseOwned(int n_robot);

    private:
        std::array<std::array<int, GRID_SIZE * GRID_SIZE>, NUM_LAYERS> m_aOwner;
    };
}

#endif
