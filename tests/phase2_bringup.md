# Phase 2 CANoe bring-up procedure (designed - NOT yet executed)

Topology: one network `PT_CAN`, DBC `vehicle_v1_0.dbc`, nodes POWERTRAIN_ECU, BRAKE_ECU, BMS_ECU, CLUSTER_ECU (CAPL files in `capl/`, include path `capl/`). Add Trace + Statistics + Logging (ASC) blocks.
Keys (click the simulation window first): `s` start drive, `u`/`d` torque +/-20 Nm, `w`/`q` speed +/-1 m/s, `b` brake pedal toggle.
Fault-like stimuli in Phase 2 are done manually: **unload/disable a node in Simulation Setup** (ECU unavailable) - proper injection is Phase 4.

| ID | Req. | Steps | Expected | Actual |
|---|---|---|---|---|
| TC-210 | build | Compile all CAPL nodes | 0 errors (report errors to fix) | not executed |
| TC-211 | CAN-REQ-006 | Run 60 s idle; export ASC; `python python/main.py periodicity log.asc` | all cyclic messages `Period OK`, no timeout gaps, 0 CRC/counter errors | not executed |
| TC-212 | CAN-REQ-007 | Observe 0x302/0x401 trace | heartbeat 500 ms (+/- 10 %) | not executed |
| TC-213 | PT policy | After 1 s press `s`, `u` x3 | PT_State DRIVE (3), MotorTorqueActual rises toward 60 Nm | not executed |
| TC-214 | PT brake override | `b` while torque requested | MotorTorqueRequest = 0 while brake applied | not executed |
| TC-215 | CAN-REQ-008, F05 | Disable BMS_ECU node during run | after ~150-300 ms PT_State FAULT (5), torque 0; CLUSTER Warn_Battery + Warn_CommLoss; PT/CLUSTER log `DTC D101 set` | not executed |
| TC-216 | F02 | Disable BRAKE_ECU node | PT DEGRADED (4), torque <= 100 Nm; Warn_Brake; DTC D100 | not executed |
| TC-217 | heal | Re-enable the node | after 5 good frames: `DTC ... healed`, PT_State returns to DRIVE/READY | not executed |
| TC-218 | CAN-REQ-009 | Cluster: observe DisplayedSpeed when BRAKE_ECU disabled | raw 255 (dashes) | not executed |
| TC-219 | BMS model | `s`, `u` x10, hold 30 s | SOC decreasing, BatteryCurrent > 0, BatteryVoltage < OCV; (values are simulated) | not executed |
Record for each executed test: date, CANoe version, log file name, PASS/FAIL, in `tests/test_matrix.md`.
