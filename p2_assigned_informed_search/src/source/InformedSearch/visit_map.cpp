#include "visit_map.h"

#include <queue>

namespace InformedSearch {

namespace {

// DESIGN 3.3 merge rule for a finite t_stale: four t_last values closer than this merge.
const float kMergeWindow = 10.0f;

// Best candidate so far under the tie rule (contract rule 4). Both options use it.
struct Best {
    bool is_found;
    double d2;
    long row;
    long col;

    Best() : is_found(false), d2(0.0), row(0), col(0) {}

    void Offer(double offered_d2, long offered_row, long offered_col) {
        const bool is_better =
            !is_found || offered_d2 < d2 ||
            (offered_d2 == d2 && (offered_row < row || (offered_row == row && offered_col < col)));
        if (!is_better) return;
        is_found = true;
        d2 = offered_d2;
        row = offered_row;
        col = offered_col;
    }
};

} // namespace

// ---------------------------------------------------------------- option A

GridVisitMap::GridVisitMap(const VisitMapConfig& config)
    : config_(config),
      cols_(CellsAlong(config.min_x, config.max_x, config.cell_size)),
      rows_(CellsAlong(config.min_y, config.max_y, config.cell_size)),
      touched_(0),
      operations_(0) {
    Reserve();
}

void GridVisitMap::Reserve() {
    Cell never = {kNever, kNever};
    cells_.assign(cols_ * rows_, never);
}

void GridVisitMap::InsertBatch(const std::vector<Point>& points, double t) {
    for (std::size_t i = 0; i < points.size(); ++i) {
        const Point& p = points[i];
        ++operations_;
        if (p.x < config_.min_x || p.y < config_.min_y || p.x >= config_.max_x || p.y >= config_.max_y)
            continue;
        Cell& cell = cells_[CellIndex(p.y - config_.min_y, config_.cell_size, rows_) * cols_ +
                            CellIndex(p.x - config_.min_x, config_.cell_size, cols_)];
        if (cell.t_last == kNever) ++touched_;
        if (static_cast<float>(t) > cell.t_last) cell.t_last = static_cast<float>(t);
    }
}

void GridVisitMap::Reserve(const Point& p, double radius, double t_until) {
    const double r2 = radius * radius;
    const double s = config_.cell_size;
    const std::size_t row_lo = CellIndex(p.y - radius - config_.min_y, s, rows_);
    const std::size_t row_hi = CellIndex(p.y + radius - config_.min_y, s, rows_);
    const std::size_t col_lo = CellIndex(p.x - radius - config_.min_x, s, cols_);
    const std::size_t col_hi = CellIndex(p.x + radius - config_.min_x, s, cols_);
    for (std::size_t row = row_lo; row <= row_hi; ++row) {
        for (std::size_t col = col_lo; col <= col_hi; ++col) {
            ++operations_;
            const Point c = CellCentre(config_, row, col);
            const double dx = c.x - p.x;
            const double dy = c.y - p.y;
            if (dx * dx + dy * dy > r2) continue;
            Cell& cell = cells_[row * cols_ + col];
            if (static_cast<float>(t_until) > cell.t_res_until)
                cell.t_res_until = static_cast<float>(t_until);
        }
    }
}

// Rings of Chebyshev index distance k around the robot cell. Every cell of ring k is at
// least (k - 1) * s from the robot (the robot may sit anywhere inside its own cell, or
// outside the grid). Stop when that bound passes the best answer. A tie keeps the ring
// going, so the lowest row then lowest column wins.
bool GridVisitMap::NearestAvailable(const Point& origin, double now, Point* target) {
    const long row0 = static_cast<long>(CellIndex(origin.y - config_.min_y, config_.cell_size, rows_));
    const long col0 = static_cast<long>(CellIndex(origin.x - config_.min_x, config_.cell_size, cols_));
    const long rows = static_cast<long>(rows_);
    const long cols = static_cast<long>(cols_);
    const long k_max = (rows > cols ? rows : cols);

    Best best;
    for (long k = 0; k <= k_max; ++k) {
        if (best.is_found) {
            const double bound = (k - 1) * config_.cell_size;
            if (bound > 0.0 && bound * bound > best.d2) break;
        }
        const long r_lo = row0 - k, r_hi = row0 + k, c_lo = col0 - k, c_hi = col0 + k;
        for (long row = r_lo < 0 ? 0 : r_lo; row <= r_hi && row < rows; ++row) {
            const bool is_edge_row = (row == r_lo || row == r_hi);
            const long step = is_edge_row ? 1 : (c_hi - c_lo > 0 ? c_hi - c_lo : 1);
            for (long col = c_lo; col <= c_hi; col += step) {
                if (col < 0 || col >= cols) continue;
                ++operations_;
                const std::size_t r = static_cast<std::size_t>(row);
                const std::size_t c = static_cast<std::size_t>(col);
                const Cell& cell = cells_[r * cols_ + c];
                if (IsCellExcluded(config_, r, c) || AvailAt(config_, cell.t_last, cell.t_res_until) > now)
                    continue;
                best.Offer(BoxDistanceSquared(origin, CellBox(config_, r, c, 1)), row, col);
            }
        }
    }
    if (!best.is_found) return false;
    *target = CellCentre(config_, static_cast<std::size_t>(best.row), static_cast<std::size_t>(best.col));
    return true;
}

void GridVisitMap::Clear() {
    Reserve();
    touched_ = 0;
    operations_ = 0;
}

// ---------------------------------------------------------------- option B

QuadtreeVisitMap::QuadtreeVisitMap(const VisitMapConfig& config, bool is_merge_on)
    : config_(config),
      cols_(CellsAlong(config.min_x, config.max_x, config.cell_size)),
      rows_(CellsAlong(config.min_y, config.max_y, config.cell_size)),
      root_size_(1),
      is_merge_on_(is_merge_on),
      touched_(0),
      operations_(0) {
    while (root_size_ < cols_ || root_size_ < rows_) root_size_ *= 2;
    Reserve();
}

static_assert(sizeof(std::int32_t) + 3 * sizeof(float) == 16, "node must be 16 bytes");

void QuadtreeVisitMap::Reserve() {
    const Node root = {-1, kNever, kNever, kNever};
    nodes_.assign(1, root);
    free_blocks_.clear();
}

std::int32_t QuadtreeVisitMap::AllocateChildren() {
    if (!free_blocks_.empty()) {
        const std::int32_t block = free_blocks_.back();
        free_blocks_.pop_back();
        return block;
    }
    const std::int32_t block = static_cast<std::int32_t>(nodes_.size());
    nodes_.resize(nodes_.size() + 4);
    return block;
}

// Children copy the parent's two times and a_min, so the split changes no answer.
void QuadtreeVisitMap::Split(std::int32_t node) {
    const Node parent = nodes_[node];
    const std::int32_t block = AllocateChildren();
    const Node child = {-1, parent.t_last, parent.t_res_until, parent.a_min};
    for (int q = 0; q < 4; ++q) nodes_[block + q] = child;
    nodes_[node].first_child = block;
}

void QuadtreeVisitMap::RefreshMin(std::int32_t node) {
    const std::int32_t block = nodes_[node].first_child;
    float smallest = nodes_[block].a_min;
    for (int q = 1; q < 4; ++q)
        if (nodes_[block + q].a_min < smallest) smallest = nodes_[block + q].a_min;
    nodes_[node].a_min = smallest;
}

// Merge 4 leaf children that are all visited and (t_stale infinite, or close in time).
// The parent keeps the oldest t_last: it becomes available first, never too late.
void QuadtreeVisitMap::TryMerge(std::int32_t node) {
    if (!is_merge_on_) return;
    const std::int32_t block = nodes_[node].first_child;
    float t_min = nodes_[block].t_last, t_max = t_min;
    float res_min = nodes_[block].t_res_until, res_max = res_min;
    for (int q = 0; q < 4; ++q) {
        const Node& child = nodes_[block + q];
        if (child.first_child >= 0 || child.t_last == kNever) return;
        if (child.t_last < t_min) t_min = child.t_last;
        if (child.t_last > t_max) t_max = child.t_last;
        if (child.t_res_until < res_min) res_min = child.t_res_until;
        if (child.t_res_until > res_max) res_max = child.t_res_until;
    }
    const bool is_stale_infinite = std::isinf(config_.t_stale);
    if (!is_stale_infinite && (t_max - t_min >= kMergeWindow || res_min != res_max)) return;
    const Node merged = {-1, t_min, res_max, AvailAt(config_, t_min, res_max)};
    nodes_[node] = merged;
    free_blocks_.push_back(block);
}

void QuadtreeVisitMap::InsertAt(std::int32_t node, std::size_t row0, std::size_t col0, std::size_t size,
                                std::size_t row, std::size_t col, float t) {
    ++operations_;
    if (nodes_[node].first_child < 0) {
        if (size == 1) {
            Node& leaf = nodes_[node];
            if (leaf.t_last == kNever) ++touched_;
            if (t > leaf.t_last) leaf.t_last = t;
            leaf.a_min = AvailAt(config_, leaf.t_last, leaf.t_res_until);
            return;
        }
        // A merged leaf is fully visited. With t_stale infinite a new visit changes nothing.
        if (std::isinf(config_.t_stale) && nodes_[node].t_last != kNever) return;
        Split(node);
    }
    const std::size_t half = size / 2;
    const int q = (row >= row0 + half ? 2 : 0) | (col >= col0 + half ? 1 : 0);
    InsertAt(nodes_[node].first_child + q, row0 + (q >> 1) * half, col0 + (q & 1) * half, half, row, col, t);
    RefreshMin(node);
    TryMerge(node);
}

void QuadtreeVisitMap::InsertBatch(const std::vector<Point>& points, double t) {
    for (std::size_t i = 0; i < points.size(); ++i) {
        const Point& p = points[i];
        if (p.x < config_.min_x || p.y < config_.min_y || p.x >= config_.max_x || p.y >= config_.max_y) {
            ++operations_;
            continue;
        }
        InsertAt(0, 0, 0, root_size_, CellIndex(p.y - config_.min_y, config_.cell_size, rows_),
                 CellIndex(p.x - config_.min_x, config_.cell_size, cols_), static_cast<float>(t));
    }
}

// Split down only where the disk cuts a block. A block whose cell centres all lie inside
// the disk takes the reservation as one leaf.
void QuadtreeVisitMap::ReserveAt(std::int32_t node, std::size_t row0, std::size_t col0, std::size_t size,
                                 const Point& p, double radius, float t_until) {
    ++operations_;
    const double r2 = radius * radius;
    const Point lo = CellCentre(config_, row0, col0);
    const Point hi = CellCentre(config_, row0 + size - 1, col0 + size - 1);
    const Box centres = {lo.x, lo.y, hi.x, hi.y};
    if (BoxDistanceSquared(p, centres) > r2) return;
    const double far_x = std::fmax(std::fabs(p.x - lo.x), std::fabs(p.x - hi.x));
    const double far_y = std::fmax(std::fabs(p.y - lo.y), std::fabs(p.y - hi.y));
    const bool is_all_inside = far_x * far_x + far_y * far_y <= r2;

    if (nodes_[node].first_child < 0) {
        if (size == 1 || is_all_inside) {
            Node& leaf = nodes_[node];
            if (t_until > leaf.t_res_until) leaf.t_res_until = t_until;
            leaf.a_min = AvailAt(config_, leaf.t_last, leaf.t_res_until);
            return;
        }
        Split(node);
    }
    const std::size_t half = size / 2;
    for (int q = 0; q < 4; ++q)
        ReserveAt(nodes_[node].first_child + q, row0 + (q >> 1) * half, col0 + (q & 1) * half, half, p,
                  radius, t_until);
    RefreshMin(node);
}

void QuadtreeVisitMap::Reserve(const Point& p, double radius, double t_until) {
    ReserveAt(0, 0, 0, root_size_, p, radius, static_cast<float>(t_until));
}

namespace {

// Heap entry: a real node, or a virtual quarter of a leaf (node = -1, avail copied from the leaf).
struct Entry {
    double d2;
    std::int32_t node;
    std::size_t row0, col0, size;
    float avail;
};

// Min-heap on box distance. The row and column only make the order deterministic.
struct EntryLater {
    bool operator()(const Entry& a, const Entry& b) const {
        if (a.d2 != b.d2) return a.d2 > b.d2;
        if (a.row0 != b.row0) return a.row0 > b.row0;
        return a.col0 > b.col0;
    }
};

} // namespace

// Best-first by box distance. A node with avail > now holds nothing available and is never
// pushed. A leaf larger than one cell is opened into 4 virtual quarters, so partly excluded
// blocks (nest disk, range edge) and ties resolve at the cell level with the same rule as A.
// The loop keeps popping while the next distance equals the best one, to apply the tie rule.
bool QuadtreeVisitMap::NearestAvailable(const Point& origin, double now, Point* target) {
    Best best;
    std::priority_queue<Entry, std::vector<Entry>, EntryLater> heap;

    // Blocks wholly outside the grid have every centre beyond max_x or max_y: excluded.
    const auto push = [&](std::int32_t node, std::size_t row0, std::size_t col0, std::size_t size,
                          float avail) {
        if (row0 >= rows_ || col0 >= cols_ || avail > now) return;
        const double d2 = BoxDistanceSquared(origin, CellBox(config_, row0, col0, size));
        if (best.is_found && d2 > best.d2) return;
        const Entry entry = {d2, node, row0, col0, size, avail};
        heap.push(entry);
    };

    push(0, 0, 0, root_size_, nodes_[0].a_min);
    while (!heap.empty()) {
        const Entry e = heap.top();
        if (best.is_found && e.d2 > best.d2) break;
        heap.pop();
        ++operations_;
        if (e.size == 1) {
            if (!IsCellExcluded(config_, e.row0, e.col0))
                best.Offer(e.d2, static_cast<long>(e.row0), static_cast<long>(e.col0));
            continue;
        }
        const std::size_t half = e.size / 2;
        const bool is_internal = e.node >= 0 && nodes_[e.node].first_child >= 0;
        for (int q = 0; q < 4; ++q) {
            const std::int32_t child = is_internal ? nodes_[e.node].first_child + q : -1;
            push(child, e.row0 + (q >> 1) * half, e.col0 + (q & 1) * half, half,
                 is_internal ? nodes_[child].a_min : e.avail);
        }
    }
    if (!best.is_found) return false;
    *target = CellCentre(config_, static_cast<std::size_t>(best.row), static_cast<std::size_t>(best.col));
    return true;
}

void QuadtreeVisitMap::Clear() {
    Reserve();
    touched_ = 0;
    operations_ = 0;
}

} // namespace InformedSearch
