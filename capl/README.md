# CAPL sources
`common/*.cin` shared libraries (include only) - one `<ecu>.can` node program per ECU.
| File | Phase | Status |
|---|---|---|
| common/vehicle_defs.cin, common/e2e.cin | 1 | written, not compiled in CANoe |
| powertrain_ecu.can | 1 | written, not compiled in CANoe |
| brake_ecu.can, bms_ecu.can, cluster_ecu.can | 2 | planned |
| gateway_ecu.can | 3 | planned |
| diagnostics.can (UDS subset, DTC store) | 4 | planned |
| fault_injection.can (separate node, not in nominal config) | 4 | planned |
| test_functions.can / test modules | 5 | planned |
No node is validated until a CANoe run is documented in `results/`.
