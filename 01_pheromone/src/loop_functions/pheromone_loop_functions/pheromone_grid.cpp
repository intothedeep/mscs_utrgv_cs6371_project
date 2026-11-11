#include "pheromone_grid.h"
#include <algorithm>
#include <cmath>

namespace pheromone
{
    double CPheromoneGrid::EvaporationFactor(double f_half_life_s, double f_ticks_per_second)
    {
        return std::pow(0.5, 1.0 / (f_half_life_s * f_ticks_per_second));
    }

    CPheromoneGrid::CPheromoneGrid(double f_evaporation_factor) : m_fEvaporationFactor(f_evaporation_factor)
    {
        Clear();
    }

    void CPheromoneGrid::Clear()
    {
        for (auto &cLayer : m_aLayers)
            cLayer.fill(0.0);
    }

    void CPheromoneGrid::Evaporate()
    {
        for (auto &cLayer : m_aLayers)
            for (double &fValue : cLayer)
                fValue *= m_fEvaporationFactor;
    }

    int CPheromoneGrid::CellOf(double f_coordinate)
    {
        int nCell = static_cast<int>(std::floor((f_coordinate - ARENA_MIN) / CELL_M));
        return (nCell < 0 || nCell >= GRID_SIZE) ? -1 : nCell;
    }

    void CPheromoneGrid::Deposit(ELayer e_layer, double f_x, double f_y, double f_amount, double f_min_x)
    {
        int nCx = CellOf(f_x), nCy = CellOf(f_y);
        if (nCx < 0 || nCy < 0)
            return;
        for (int nDy = -1; nDy <= 1; ++nDy)
            for (int nDx = -1; nDx <= 1; ++nDx)
            {
                int nX = nCx + nDx, nY = nCy + nDy;
                if (nX < 0 || nX >= GRID_SIZE || nY < 0 || nY >= GRID_SIZE)
                    continue;
                if (ARENA_MIN + (nX + 0.5) * CELL_M < f_min_x)
                    continue; /* cell centre inside the nest */
                double &fCell = m_aLayers[e_layer][nY * GRID_SIZE + nX];
                fCell = std::max(fCell, f_amount);
            }
    }

    double CPheromoneGrid::Value(ELayer e_layer, double f_x, double f_y) const
    {
        int nX = CellOf(f_x), nY = CellOf(f_y);
        return (nX < 0 || nY < 0) ? 0.0 : m_aLayers[e_layer][nY * GRID_SIZE + nX];
    }

    double CPheromoneGrid::Probe(double f_x, double f_y) const
    {
        return Value(LAYER_TRUE, f_x, f_y) + Value(LAYER_FALSE, f_x, f_y);
    }

    double CPheromoneGrid::LayerSum(ELayer e_layer) const
    {
        double fSum = 0.0;
        for (double fValue : m_aLayers[e_layer])
            fSum += fValue;
        return fSum;
    }
}
