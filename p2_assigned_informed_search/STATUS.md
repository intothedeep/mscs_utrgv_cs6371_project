> Completed items live in `_archive/` (cold storage, do not read unless
> investigating history). This doc holds the active + planned log only.

# Status: p2_assigned_informed_search

2026-11-12 baseline: Collision_Free_CPFA cloned to vendor/ and pinned at 9480f2e (README.md, D-001)
2026-11-12 baseline: built in build_baseline/, smoke seed 1 ran 5.67 s wall, 245 collected (main session, DESIGN.md §1)
2026-11-12 research: code map and literature survey written (research/baseline_code_map.md, research/informed_search_survey.md)
2026-11-12 design: DESIGN.md draft, options A/B/C, protocol, milestones M1 to M5 (DESIGN.md)
2026-11-12 decisions: D-001 to D-011 (DECISIONS.md)
2026-11-12 plan: PLAN.md, TASKS.md, RQ.md created, M1 to M5, 49 tasks open (PLAN.md, TASKS.md)
2026-11-12 decisions: D-012 to D-014; baseline configure command in README.md (DECISIONS.md)
2026-11-12 M1-10: mock S3 criteria file written, mock true, DESIGN §6.2 items 1 to 8 (prereg/S3_eval_MOCK.json)
2026-11-12 M3-01: visit_map interface and option A (GridVisitMap), static AC only, not built (src/source/InformedSearch/visit_map.{h,cpp})
2026-11-12 M3-02: option B QuadtreeVisitMap, shared contract helpers in visit_map.h, static AC only, syntax check clean (visit_map.{h,cpp})
2026-11-12 M1-01: pyproject.toml, .gitignore lines for mock/runs and build_ours (developer)
2026-11-12 M1-02: tools/schema.py, tools/run_io.py (developer)
2026-11-12 M1-03: tools/check_runs.py (developer)
2026-11-12 M1-04: tools/collect_runs.py (developer, D-013)
2026-11-12 M1-05: tools/make_mock_runs.py (developer)
2026-11-12 decisions: D-015, D-016 (DECISIONS.md)
2026-11-12 M1: D-015 header-only arms applied (schema, mock), .venv ignored, .python-version 3.12.12 (developer)
2026-11-12 M1-06..08: tools/analyze.py, analyze_figures.py, plot_style.py, report.py, report_html.py; verified on scratchpad mirror, repo gate pending (developer)
2026-11-12 decisions: D-017 folder rename, D-018 hybrid tuning candidate, D-019 irrigation analogy, D-020 index.html name (DECISIONS.md)
