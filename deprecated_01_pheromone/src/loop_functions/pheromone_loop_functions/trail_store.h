#ifndef TRAIL_STORE_H
#define TRAIL_STORE_H

#include <vector>

/*
 * Trail records of the ID arm (DESIGN_M6 section 3.1). One record per deposit run: the
 * creator index, the trail end (the first deposit of the run) and its start tick.
 * Pure: no simulator header, no random draw. Records stay in the order they were added,
 * which is (start tick, creator) because the caller adds robots in index order each tick.
 */
namespace pheromone
{
    struct STrail
    {
        int id;        /* unique, never reused: a check keeps it after the record is gone */
        int creator;   /* robot index */
        double x, y;   /* the trail end */
        int startTick;
        double extraS; /* est_extra_s: estimate feedback of late returns (section 3.2) */
    };

    class CTrailStore
    {
    public:
        explicit CTrailStore(int n_expiry_ticks);

        int Add(int n_creator, double f_x, double f_y, int n_tick);
        /* Drops records older than the expiry. True when it dropped any. */
        bool Expire(int n_tick);
        void RemoveCreator(int n_creator);
        /* Adds to est_extra_s of a record. False when the record is gone. */
        bool AddExtra(int n_id, double f_seconds);

        const std::vector<STrail> &Active() const { return m_vecTrails; }
        /* nullptr when the record is gone. */
        const STrail *Find(int n_id) const;
        /* The record with the highest start tick of this creator, nullptr if none. */
        const STrail *LatestOf(int n_creator) const;

    private:
        int m_nExpiryTicks;
        int m_nNextId;
        std::vector<STrail> m_vecTrails;
    };
}

#endif
