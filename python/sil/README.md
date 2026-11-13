# Python SIL (no Vector tools needed)
Python port of the Phase 2 CAPL ECUs on a deterministic simulated-time bus (1 ms steps), same DBC, same E2E.
```
python python/main.py sil all              # run all scenarios, print DTC events, write results/sil/<name>.asc
python python/main.py sil f02_brake_timeout --report   # + periodicity table of the generated log
python -m pytest tests/sil -q
```
Scenarios: nominal, f01_single_frame_loss, f02_brake_timeout, f03_speed_invalid, f04_voltage_out_of_range,
f05_bms_unavailable, f07a_counter_fault, f07b_crc_fault, brake_override.
Faults are injected on the wire (`scenarios.py` interceptors) or by disabling a node; ECU code has no test hooks.
**What this proves / does not prove:** it verifies the supervision and degradation *design* (timeouts, debounce, E2E, policy).
It does not validate the CAPL source, CANoe behaviour, arbitration, bit timing, or a vehicle. All results are SIMULATED.
Generated `.asc` logs can be fed to `python python/main.py periodicity <file>` like CANoe exports.
