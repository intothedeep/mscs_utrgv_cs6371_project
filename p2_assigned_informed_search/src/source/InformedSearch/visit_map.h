#ifndef VISIT_MAP_H
#define VISIT_MAP_H

// Visit map for informed search (DESIGN 3.1 to 3.3). PURE: no ARGoS include, so the
// simulation and the stand-alone benchmark run the same code.
// One interface (VisitMap). GridVisitMap is option A, QuadtreeVisitMap is option B.
//
// Contract shared by every option (so A and B give the same answers at 10 m):
//   1. Exclusion by cell centre: a cell is never an answer when its centre lies inside
//      the nest disk (distance <= nest_radius) or beyond max_x or max_y.
//   2. Reserve(p, r, t_until) covers exactly the minimum cells whose centre is within r of p.
//   3. InsertBatch drops every point outside [min_x, max_x) x [min_y, max_y).
//   4. Query tie rule: smallest box distance, then lowest row, then lowest column.
// The shared helpers below carry these rules, so no option re-implements them.

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

namespace InformedSearch {

struct Point {
    double x;
    double y;
};

// Forage range, nest exclusion disk and the two time constants.
struct VisitMapConfig {
    double min_x, min_y, max_x, max_y; // forage range (base.cpp ForageRange)
    double cell_size;                  // minimum cell side s_min
    Point  nest;                       // nest exclusion disk centre
    double nest_radius;                // see contract rule 1
    double t_stale;                    // seconds a visit blocks a cell. +infinity = forever
};

struct Box {
    double x0, y0, x1, y1;
};

constexpr float kNever = -std::numeric_limits<float>::infinity();

// Number of minimum cells along one axis.
inline std::size_t CellsAlong(double lo, double hi, double cell_size) {
    return static_cast<std::size_t>(std::ceil((hi - lo) / cell_size));
}

// Index of the minimum cell holding offset (distance from the range minimum), clamped.
inline std::size_t CellIndex(double offset, double cell_size, std::size_t count) {
    if (!(offset > 0.0)) return 0;
    const std::size_t index = static_cast<std::size_t>(offset / cell_size);
    return index >= count ? count - 1 : index;
}

inline Point CellCentre(const VisitMapConfig& c, std::size_t row, std::size_t col) {
    const Point centre = {c.min_x + (col + 0.5) * c.cell_size, c.min_y + (row + 0.5) * c.cell_size};
    return centre;
}

// Box of the size x size block of minimum cells whose first cell is (row0, col0).
inline Box CellBox(const VisitMapConfig& c, std::size_t row0, std::size_t col0, std::size_t size) {
    const Box box = {c.min_x + col0 * c.cell_size, c.min_y + row0 * c.cell_size,
                     c.min_x + (col0 + size) * c.cell_size, c.min_y + (row0 + size) * c.cell_size};
    return box;
}

// Contract rule 1.
inline bool IsCellExcluded(const VisitMapConfig& c, std::size_t row, std::size_t col) {
    const Point p = CellCentre(c, row, col);
    if (p.x > c.max_x || p.y > c.max_y) return true;
    const double dx = p.x - c.nest.x;
    const double dy = p.y - c.nest.y;
    return dx * dx + dy * dy <= c.nest_radius * c.nest_radius;
}

// Squared Euclidean distance from p to the box (DESIGN 3.1 query rule).
inline double BoxDistanceSquared(const Point& p, const Box& b) {
    const double dx = p.x < b.x0 ? b.x0 - p.x : (p.x > b.x1 ? p.x - b.x1 : 0.0);
    const double dy = p.y < b.y0 ? b.y0 - p.y : (p.y > b.y1 ? p.y - b.y1 : 0.0);
    return dx * dx + dy * dy;
}

// avail_at = max(t_last + t_stale, t_res_until) (DESIGN 3.1 step 3). Available when <= now.
// A never-visited cell has t_last = -inf: skip the sum, -inf + inf is NaN.
inline float AvailAt(const VisitMapConfig& c, float t_last, float t_res_until) {
    const double stale_until = t_last == kNever ? -std::numeric_limits<double>::infinity()
                                                : static_cast<double>(t_last) + c.t_stale;
    const double res_until = t_res_until;
    return static_cast<float>(stale_until > res_until ? stale_until : res_until);
}

class VisitMap {
public:
    virtual ~VisitMap() {}

    // Pre-allocate for the configured area. Does not change answers.
    virtual void Reserve() = 0;
    // Record every point as visited at upload time t (t_last = max(t_last, t)).
    virtual void InsertBatch(const std::vector<Point>& points, double t) = 0;
    // Reserve the minimum cells whose centre is within radius of p until t_until.
    virtual void Reserve(const Point& p, double radius, double t_until) = 0;
    // Nearest available cell to origin at time now. Writes its centre to *target and
    // returns true. Returns false when no cell is available.
    virtual bool NearestAvailable(const Point& origin, double now, Point* target) = 0;
    // Forget every visit and reservation, and zero the operation counter.
    virtual void Clear() = 0;

    virtual std::size_t NodeCount() const = 0;        // allocated cells or live nodes
    virtual std::size_t MemoryBytes() const = 0;      // bytes of map storage
    virtual std::size_t TouchedCellCount() const = 0; // minimum cells with a recorded visit
    // Cumulative work units since Clear(): one per cell or node examined, one per point inserted.
    // Callers take differences around a call to cost it.
    virtual std::uint64_t Operations() const = 0;
};

// Option A: fine uniform grid, square ring search outward from the robot cell.
class GridVisitMap : public VisitMap {
public:
    explicit GridVisitMap(const VisitMapConfig& config);

    void Reserve() override;
    void InsertBatch(const std::vector<Point>& points, double t) override;
    void Reserve(const Point& p, double radius, double t_until) override;
    bool NearestAvailable(const Point& origin, double now, Point* target) override;
    void Clear() override;

    std::size_t NodeCount() const override { return cols_ * rows_; }
    std::size_t MemoryBytes() const override { return cols_ * rows_ * sizeof(Cell); }
    std::size_t TouchedCellCount() const override { return touched_; }
    std::uint64_t Operations() const override { return operations_; }

private:
    struct Cell {
        float t_last;      // kNever = never visited
        float t_res_until; // kNever = never reserved
    };

    VisitMapConfig config_;
    std::size_t cols_;
    std::size_t rows_;
    std::vector<Cell> cells_; // row-major: index = row * cols_ + col
    std::size_t touched_;
    std::uint64_t operations_;
};

// Option B: region quadtree over a power-of-two block of minimum cells (DESIGN 3.3).
// Never-visited and fully visited space stays as large leaves. Each node keeps a_min,
// the smallest avail_at in its subtree, so a query skips whole subtrees.
class QuadtreeVisitMap : public VisitMap {
public:
    // is_merge_on = false is benchmark structure 6 (DESIGN 5.2).
    QuadtreeVisitMap(const VisitMapConfig& config, bool is_merge_on = true);

    void Reserve() override;
    void InsertBatch(const std::vector<Point>& points, double t) override;
    void Reserve(const Point& p, double radius, double t_until) override;
    bool NearestAvailable(const Point& origin, double now, Point* target) override;
    void Clear() override;

    std::size_t NodeCount() const override { return nodes_.size() - 4 * free_blocks_.size(); }
    std::size_t MemoryBytes() const override { return NodeCount() * sizeof(Node); }
    std::size_t TouchedCellCount() const override { return touched_; }
    std::uint64_t Operations() const override { return operations_; }

private:
    // 16 bytes. A leaf has first_child = -1 and holds the times. An internal node
    // points at 4 contiguous children (quadrant q = 2 * is_lower_row + is_right_col).
    struct Node {
        std::int32_t first_child;
        float t_last;
        float t_res_until;
        float a_min;
    };

    std::int32_t AllocateChildren();
    void Split(std::int32_t node);
    void RefreshMin(std::int32_t node);
    void TryMerge(std::int32_t node);
    void InsertAt(std::int32_t node, std::size_t row0, std::size_t col0, std::size_t size,
                  std::size_t row, std::size_t col, float t);
    void ReserveAt(std::int32_t node, std::size_t row0, std::size_t col0, std::size_t size,
                   const Point& p, double radius, float t_until);

    VisitMapConfig config_;
    std::size_t cols_;
    std::size_t rows_;
    std::size_t root_size_; // side of the root block in minimum cells, a power of two
    bool is_merge_on_;
    std::vector<Node> nodes_;
    std::vector<std::int32_t> free_blocks_; // first index of each freed block of 4 children
    std::size_t touched_;
    std::uint64_t operations_;
};

} // namespace InformedSearch

#endif
