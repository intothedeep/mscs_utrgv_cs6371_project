# 02_informed_search_assigned: Final Project 2 (informed search for CPFA swarms)

- Task: `../docs/Autonomous_Mobile_Robot_Programming_Final Project 2.pdf`.
- Baseline: `https://github.com/MARSLab-UTRGV/Collision_Free_CPFA`, commit `9480f2e3cf9d0c15313286df4e6078576f441bff` (2026-05-01).
- Local clone: `vendor/Collision_Free_CPFA/` (git-ignored). Re-create it with `git clone` and `git checkout` at that commit.

## Build the baseline (main session only)

```bash
mkdir -p build_baseline && cd build_baseline
cmake ../vendor/Collision_Free_CPFA -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release
make -j1
```

- `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`: the vendor `CMakeLists.txt` says 2.8.12, which CMake 4 rejects.
