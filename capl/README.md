# CAPL sources
`common/*.cin` shared libraries (include only; include order: vehicle_defs, e2e, dtc, supervision) - one `<ecu>.can` node program per ECU.
| File | Phase | Status |
|---|---|---|
| common/vehicle_defs.cin, e2e.cin | 1 (defs extended in 2) | written, not compiled in CANoe |
| common/dtc.cin, supervision.cin | 2 | written, not compiled in CANoe |
| powertrain_ecu.can | 1, supervision added in 2 | written, not compiled in CANoe |
| brake_ecu.can, bms_ecu.can, cluster_ecu.can | 2 | written, not compiled in CANoe |
| gateway_ecu.can | 3 | planned |
| diagnostics.can (UDS subset, DTC access) | 4 | planned |
| fault_injection.can (separate node, not in nominal config) | 4 | planned |
| test_functions.can / test modules | 5 | planned |
Phase 2 bring-up topology: POWERTRAIN, BRAKE, BMS and CLUSTER all on one network (PT_CAN) until the gateway exists.
No node is validated until a CANoe run is documented in `results/`.
