# 10 - Results

## Executed results (Tier A, software)
`pytest -q` on 2026-11-12: 17 passed, 0 failed (see `tests/test_matrix.md`, TC-001..TC-008).
Analytical (not measured) bus load from the matrix: PT_CAN 7.4 % nominal / 9.0 % worst-case stuffing; INFO_CAN 5.6 % / 6.9 %.

## Not yet available
No CANoe/CANalyzer run has been performed. No measured periodicity, latency, bus load or DTC behaviour exists. Do not cite any.

## Figures to produce (label every figure "measured", "simulated" or "analytical")
| # | Figure | Source | Phase | State |
|---|---|---|---|---|
| F1 | CAN network architecture (PT_CAN / INFO_CAN) | Mermaid in doc 02, exported PNG | 1 | diagram in doc 02 |
| F2 | ECU communication matrix diagram | generated from `can_matrix.csv` | 2 | not generated |
| F3 | CAN frame example with E2E bytes (PT_Status) | Python/cantools encode | 5 | not generated |
| F4 | Message timing / jitter histogram | CANalyzer log + Python | 5 | not generated |
| F5 | Bus load vs time | CANalyzer statistics | 5 | not generated |
| F6 | Signal plots (VehicleSpeed, torque, SOC, voltage) | log + Python (label simulated) | 5 | not generated |
| F7 | Fault detection timeline (F02, F05) | log | 5 | not generated |
| F8 | DTC detection screenshot | CANoe/tester trace | 4 | not generated |
| F9 | Test result summary | pytest + CANoe reports | 6 | partial (pytest only) |
| F10 | Gateway routing proof (same frame on both buses, latency) | trace | 3 | not generated |
| F11 | Diagnostic sequence diagram + trace | Mermaid + trace | 4 | not generated |
Screenshots to capture later: CANoe Trace, Graphics, Statistics windows; CANalyzer Statistics and filter configuration; Test report.
