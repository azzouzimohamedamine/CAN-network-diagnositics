# 08 - Test Strategy

## Levels and status vocabulary (TEST-REQ-003)
| Status | Meaning |
|---|---|
| **Executed-SW** | Run by pytest on the DBC/Python code. Real result recorded. |
| **Designed** | Specified, not yet run. Actual result = "not executed". |
| **Simulated (CANoe SIL)** | Run in CANoe/CANalyzer on virtual channels (none yet). |
| **HW-unavailable** | Needs real ECU/vehicle/HIL; out of scope for Project 1. |
Virtual tests are never reported as physical tests (SIM-REQ-002).

## Test types
Functional (nominal signals/periodicity/routing/diagnostics), Negative (invalid requests, invalid signals), Boundary (min/max/invalid raw of a signal), Timeout, Fault injection (F01-F08), Regression (golden log replay + generator drift + DBC compatibility).

## Procedure
1. Tier A (any machine): `pytest -q` -> TC-001..TC-008 (also run in CI later).
2. Tier B (CANoe): load `vehicle_v1_0.dbc` on both networks, run nodes, run test module or injector scenario, export log (ASC/BLF) to `results/sample_logs/` (small, reviewed files only).
3. Analyse logs with Python (Phase 5): frequency, missing messages, E2E, report to `results/`.
4. Update `tests/test_matrix.md` with the *actual* result, date, tool versions, log file name. A row without a log or pytest output stays "not executed".

Full matrix: [`../tests/test_matrix.md`](../tests/test_matrix.md). Traceability: [09](09_traceability_matrix.md).
