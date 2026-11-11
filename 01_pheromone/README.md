# 01_pheromone: how to build and run

Pheromone foraging under misleading trails. Design: [DESIGN.md](./DESIGN.md). Plan: [PLAN.md](./PLAN.md).
All commands start in `submodule_project/01_pheromone/` unless a `cd` says otherwise.
Python runs as `OMP_NUM_THREADS=1 timeout 300 uv run python ...` (one core, 5 minutes, D-012).

## Folders and runs roots

| Runs root | Holds | Git |
| --- | --- | --- |
| `mock/runs/` | 80 MOCK runs from `make_mock_runs.py` | ignored (D-014) |
| `runs/smoke/` | 1-seed smoke runs | ignored |
| `runs/tuning/` | pheromone tuning rounds (D-007) | ignored |
| `runs/judgement/` | keep-A judgement, 6 runs (D-010) | ignored |
| `results/<mock\|real>/` | charts, tables, pages | committed |
| `prereg/` | pre-registrations | committed |

## 1. Build

```bash
cd src
mkdir -p build && cd build
cmake ..
make -j2
```

- Result: `src/build/controllers/pheromone_forager/libpheromone_forager.dylib` and `src/build/loop_functions/pheromone_loop_functions/libpheromone_loop_functions.so`.
- Run every `argos3` command from `src/`. Library paths in the `.argos` files are relative to `src/`.

## 2. Qt demo

```bash
cd src
argos3 -c experiments/pheromone_qt.argos
```

- Green trails form behind carrying robots and fade. Black cylinder = robot carries food.
- It writes no run log (no `<logger>` node).

## 3. Headless smoke run (runs root `runs/smoke/`)

```bash
OMP_NUM_THREADS=1 timeout 300 uv run python tools/make_sweep.py --cell 0,0,1 --root runs/smoke
cd src
argos3 -c experiments/generated/<runid>.argos       # <runid> is printed by make_sweep.py
cd ..
OMP_NUM_THREADS=1 timeout 300 uv run python tools/check_runs.py runs/smoke --log results/real/check_log.txt
OMP_NUM_THREADS=1 timeout 300 uv run python tools/analyze.py runs/smoke
```

- `make_sweep.py` needs the built libraries. It stamps the git commit and library hashes into the `.argos` file.
- Only d = 0 works until M3 (detractor controller).

## 4. Tools (in `tools/`)

| Tool | Command | Reads, writes |
| --- | --- | --- |
| `make_mock_runs.py` | `uv run python tools/make_mock_runs.py` | writes `mock/runs/` |
| `check_runs.py` | `uv run python tools/check_runs.py <runs root> [--log FILE]` | reads a runs root, exit 0 when all pass |
| `analyze.py` | `uv run python tools/analyze.py <runs root>` | writes `results/mock/` or `results/real/` |
| `make_report.py` | `uv run python tools/make_report.py --phase mvp1` or `--phase mvp2` | reads saved outputs, writes `results/<mock\|real>/<phase>/` |
| `make_sweep.py` | see section 3 | writes `src/experiments/generated/` |

## 5. Pheromone tuning (D-007, runs root `runs/tuning/`)

1. Commit `prereg/pheromone_tuning.md`. The scripts refuse to run before.
2. Round 1, start values (half-life 60 s, `lambda_dep` 0.077): `uv run python tools/make_tuning.py --round 1 --run`
3. Rounds 2 and 3 change one value from the best round, for example: `uv run python tools/make_tuning.py --round 2 --half-life 120 --run`
4. Pick: `uv run python tools/tuning_pick.py` writes `results/real/tuning/tuning_pick.json`.

- Each round is d = 0, defense off, seeds 101 to 103. The runs go one at a time, 300 s each (D-013).

## 6. Keep-A judgement (D-010, runs root `runs/judgement/`)

1. Commit `prereg/keep_a_judgement.md`. Freeze the tuning pick first.
2. Runs: `uv run python tools/make_judgement.py --run` (6 runs, seeds 104 to 106). It runs once.
3. Verdict: `uv run python tools/judge_keep_a.py` writes `results/real/judgement/verdict.json`.

- Arm 1 is pheromone on. Arm 2 sets the controller attribute `follow_enabled="false"` in `<params><pheromone .../>`, which makes `theta_on` infinite (no following).
