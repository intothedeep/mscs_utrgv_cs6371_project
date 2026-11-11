#include "owner_grid.h"

namespace pheromone
{
    COwnerGrid::COwnerGrid()
    {
        Clear();
    }

    void COwnerGrid::Clear()
    {
        for (auto &cLayer : m_aOwner)
            cLayer.fill(-1);
    }

    void COwnerGrid::SetOwner(ELayer e_layer, int n_cell, int n_robot)
    {
        m_aOwner[e_layer][n_cell] = n_robot;
    }

    int COwnerGrid::Owner(ELayer e_layer, int n_cell) const
    {
        return m_aOwner[e_layer][n_cell];
    }

    int COwnerGrid::Dominant(int n_cell, double f_true, double f_false) const
    {
        const bool bTrue = f_true >= f_false;
        if ((bTrue ? f_true : f_false) <= 0.0)
            return -1;
        return Owner(bTrue ? LAYER_TRUE : LAYER_FALSE, n_cell);
    }

    std::vector<COwnerGrid::TCell> COwnerGrid::ReleaseOwned(int n_robot)
    {
        std::vector<TCell> vecCells;
        for (int nLayer = 0; nLayer < NUM_LAYERS; ++nLayer)
            for (int nCell = 0; nCell < GRID_SIZE * GRID_SIZE; ++nCell)
                if (m_aOwner[nLayer][nCell] == n_robot)
                {
                    m_aOwner[nLayer][nCell] = -1;
                    vecCells.emplace_back(nLayer, nCell);
                }
        return vecCells;
    }
}
