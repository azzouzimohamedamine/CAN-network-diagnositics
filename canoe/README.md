# CANoe configuration guide (to be executed by the user - no binary .cfg committed)
Status: **designed, not executed.** Requires a Vector CANoe licence/edition of your own.
1. New configuration; two virtual CAN channels: **PT_CAN**, **INFO_CAN** (500 kbit/s).
2. Associate `can_database/vehicle_v1_0.dbc` with both networks.
3. Simulation Setup -> add nodes with the CAPL files: PT_CAN: POWERTRAIN_ECU (`capl/powertrain_ecu.can`), later BRAKE/BMS; both networks: GATEWAY_ECU; INFO_CAN: CLUSTER_ECU, DIAG_TESTER. Set the CAPL include path to `capl/`.
4. Measurement Setup: Trace (per network), Graphics (VehicleSpeed, MotorTorqueActual, SOC), Statistics, Data window; Logging block -> `results/` (exclude from Git unless a small reviewed log is added with `git add -f`).
5. Panels (Phase 2): driver inputs, fault switches, DTC display (system variables namespace `Veh::`).
6. Run 60 s, capture trace; check periodicity and E2E bytes manually, then analyse in Python.
First check (Phase 1): PT_Status every 20 ms, PT_Torque every 10 ms, byte 7 = CRC matching `python/can_analysis/e2e.py`.

## Phase 2 bring-up topology
Single network `PT_CAN` with POWERTRAIN_ECU, BRAKE_ECU, BMS_ECU and CLUSTER_ECU (no gateway yet; CLUSTER moves to INFO_CAN in Phase 3).
Procedure and expected results: `tests/phase2_bringup.md`. Include path must contain `capl/` so `common/*.cin` resolve.
