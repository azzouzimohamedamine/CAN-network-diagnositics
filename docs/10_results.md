# 10 - Results

## Executed results (Tier A, software)
`pytest -q`: 23 passed, 0 failed (`tests/test_matrix.md`): TC-001..TC-008 on the DBC/E2E code, TC-201..TC-206 on **synthetic** logs (they test the analysis code, not the vehicle).
Analytical (not measured) bus load from the matrix: PT_CAN 7.4 % nominal / 9.0 % worst-case stuffing; INFO_CAN 5.6 % / 6.9 %.

## Python SIL results (simulated, `python python/main.py sil all`)
`pytest -q`: 33 passed in total. TC-301..TC-310 run the Python port of the Phase 2 ECUs with faults injected on the wire. They are **simulated** results about the design, not about the CAPL code or a vehicle. Findings:
1. **Design defect found and fixed:** the first policy degraded the powertrain as soon as the VehicleSpeed DTC was confirmed (about 20 ms) instead of holding the last valid value for 500 ms (docs 05/07). Corrected in both the Python port and `powertrain_ecu.can`.
2. **Detection latency** for a timeout is "timeout + up to one 10 ms supervision tick" (70 ms for a 60 ms timeout in TC-303), not exactly the timeout.
3. **Slow recovery from a BMS outage:** heal needs 5 good `BMS_Faults` frames at a 500 ms heartbeat, so PT stays in FAULT about 2.5 s after the BMS returns (TC-304). Candidate change for a later version: heal on the fast `BMS_Measurements` (50 ms) instead.

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
